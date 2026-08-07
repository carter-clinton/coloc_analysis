---
task: quick/260806-sr4
verified: 2026-08-06T00:00:00Z
status: passed
score: 10/10 verification items demonstrated
verifier_mode: goal-backward, adversarial (independent fixtures, not the executor's)
commits_verified: [98e0ee9, 656529a, c04e672, 5f0520b]
baseline_rev: 1b5b8c6
branch: m3-W2-aou-deltas
method: >
  Every claim below was DEMONSTRATED by perturbation, not read off the source.
  All perturbations are in-memory through the `actual_text=` seam; the working
  tree was md5-checked before and after every script and never moved.
  The full `tests/m3` suite was NOT run (orchestrator running it in parallel).
gaps: []
advisories:
  - id: ADV-1
    severity: info
    item: "`tests/m3/test_source_freeze_pins.py:395` contains the literals `FROZEN_R_REV` and `FREEZE_REF` inside a comment narrating the pre-rescope constant count."
    why_not_a_gap: "Prose only. No symbol resolves; the bare-old-name grep gate in T2 STEP 5 was aimed at live consumers, and there are zero. Verified: no assignment, no import, no reference."
  - id: ADV-2
    severity: info
    item: "`_assert_r_freeze_clean`'s docstring and `source_freeze.py`'s module docstring both cite the mid-test call sites as `:341`/`:357`. Post-rewire they are at `:367` and `:381`."
    why_not_a_gap: "Stale line numbers in prose. The call sites themselves are byte-unchanged from the base and both are still live (verified against `1b5b8c6`)."
  - id: ADV-3
    severity: info
    item: "JOB A at the mid-test site no longer detects a leaked COMMENT onto the working tree; the old byte gate did."
    why_not_a_gap: "This IS the authorized rescope (AUTH-SR4-RESCOPE), recorded in DEC-2026-08-06-sr4-freeze-scope. The byte-sensitivity it gives up at JOB A is retained (and strengthened, SHA-free) at both JOB B sites, which are the sites that actually alter source in memory. Not an unauthorized weakening under hard rule 6."
  - id: ADV-4
    severity: info
    item: "`.planning/quick/260806-sr4-*` is UNTRACKED at HEAD -- the PLAN doc was never committed before execution, contrary to hard rule 9's stated precedent."
    why_not_a_gap: "It only made the `':!.planning/quick/260806-sr4-*'` scope-diff exclusion unnecessary. Actual scope diff = 17 files, matching D2."
---

# quick/260806-sr4 Verification Report — the source freeze rescope

**Goal:** replace the whole-file BYTE freeze on `run_susie_rss.R` with a
comment-insensitive, symbol-scoped CODE pin; close K-3 as the acceptance
demonstration; record the freeze convention in DECISIONS.md.

**Status: PASSED — 10/10.** The central question ("is the new guard actually
capable of failing?") is answered YES by demonstration, including an exhaustive
two-sided sweep the executor did not run.

---

## 1. THE CENTRAL QUESTION — the guard is capable of failing

Driven with the verifier's OWN fixtures (not the shipped ones), all in-memory.

| Perturbation | Expected | Observed |
|---|---|---|
| new statement injected into **each of the 5 pinned R symbols** | RED, message NAMES the symbol | **RED 5/5**, e.g. ``` `load_ld_matrix`: the CODE of ... :: symbol `load_ld_matrix` has MOVED off its pin bf04199``` |
| same, checked against the whole-file floor | RED | **RED 5/5** |
| comment text extended (`# THE TRAP (m3-04c Task 1b)`) | GREEN | **GREEN** |
| brand-new comment line appended at EOF | GREEN | **GREEN** |
| 3 blank lines inserted before `option_list` | GREEN | **GREEN** |
| **trailing whitespace appended to all 1,358 lines** | GREEN | **GREEN** |
| Python module docstring first line extended | GREEN | **GREEN** |
| Python code line inserted | RED | **RED** |

### The concealment hazard — both halves, four extra shapes beyond the shipped fixture

The shipped NC-SR3 uses one R and one Python carrier. I built four more
adversarial R shapes and one Python triple-quote shape:

| Concealment carrier | naive `re.sub(r"#.*$","")` blind? | `source_freeze` detects? |
|---|---|---|
| double-quoted R string (shipped fixture shape) | **True** | **True** |
| **single-quoted** R string | **True** | **True** |
| **escaped quote before the `#`** (`"a\"b#c"`) | **True** | **True** |
| `#` as the entire string (`paste0("#", "x")`) | **True** | **True** |
| nested quote kinds (`gsub("#[0-9]+","", 'v#12')`) | **True** | **True** |
| Python **non-docstring triple-quoted** string | **True** | **True** |

The hazard is therefore demonstrated real (the obvious implementation is blind
to every one of these) and the shipped utility is demonstrated not-blind to any
of them. `assert_code_frozen` was also driven end-to-end on the concealed R
fixture and went RED.

### ⭐ Exhaustive two-sided detectability sweep (verifier-added, not in the plan)

For **every one of the 1,358 physical lines** of `run_susie_rss.R`, the line was
deleted in memory and the whole-file floor asked whether it noticed:

```
file lines=1358  code-bearing=818  non-code=540  code_lines()=818

CODE-line deletions the floor MISSED (must be 0): 0
NON-CODE-line deletions the floor wrongly flagged (must be 0): 0
```

**818/818 code deletions caught. 540/540 comment/blank deletions ignored. Zero
false negatives, zero false positives.** The same sweep on
`condition_ld_matrix.py` (14 pure-comment + 34 blank lines) wrongly flagged 0.

Order sensitivity also confirmed: swapping two adjacent top-level code lines
(`:701`/`:702`) goes **RED**.

---

## 2. HARD RULE 4a / 4b — the silent-failure mode

Fixture `q <- "line1\nline2 trailing   \nend"`, driven through the SHIPPED
`_mask_r` / `_code_lines_from_mask`:

| Variant | `code_lines` | `len(masked)` |
|---|---|---|
| production (`filler="_"`, `keep_newlines=True`) | `['q <- "line1', 'line2 trailing', 'end"']` | 34 |
| **4a violated** (`keep_newlines=False`) | `['q <- "line1']` — **two lines silently vanish** | **34** |
| **4b violated** (`filler=" "`) | `['q <- "', 'end"']` — trailing content lost to `rstrip()` | 34 |

`len(text) == 34`. **The length invariant holds under BOTH violating variants —
so `len(masked) == len(text)` is provably BLIND to 4a and could never have
caught it.** That is the executor's claim and it reproduces exactly.

- **Newlines written through, even inside a string:** production mask preserves
  the newline count (2 → 2). The 4a-violating mask drops both (2 → 0).
- **Filler is non-whitespace:** `_FILLER == "_"`, `_FILLER.isspace() is False`;
  `inspect.signature(_mask_r)` confirms the production defaults ARE `filler="_",
  keep_newlines=True`.
- **A real regression guard exists, not just a test:** `_code_lines_r` carries a
  live `assert masked.count("\n") == text.count("\n")` (hard rule 4a) on every
  production call — so a future 4a regression fails loudly at the call site, not
  only in the synthetic test.
- Sanity on a realistic shape: injecting a multi-line R string into the real
  file yields exactly `['ZZ <- "aaa', 'bbb ccc', 'ddd"']`.

---

## 3. COVERAGE OF THE ~700 UNFUNCTIONED LINES

Measured, not assumed:

```
option_list <- list(  at :659;  file is 1358 lines
  regularize_ld                    :25-28
  run_susie_with_ladder            :30-67
  safe_region_id                   :69-71
  load_ld_matrix                   :142-601
  assert_declared_ld_authoritative :642-657
lines >= 659 inside NO symbol span: 700
  toJSON :938  inside a symbol? False
  toJSON :970  inside a symbol? False
  toJSON :1357 inside a symbol? False
```

**Exactly 700 lines and all three `toJSON` emits are inside no symbol.** Two
independent perturbations in that span:

| Perturbation | whole-file floor | all 5 symbol pins |
|---|---|---|
| `:1357` `pretty = TRUE` → `pretty = FALSE` | **RED** | GREEN ×5 |
| new top-level statement after `:659` `option_list <- list(` | **RED** | GREEN ×5 |

The floor catches what every symbol pin misses. Load-bearing, proven.

---

## 4. THE `ref=` WEAKENING IS CLOSED

`assert_code_frozen` rejects every symbolic/derived ref tried, each for the
right reason (`"is not an immutable revision"`):

`HEAD`, `main`, `HEAD~1`, `bf04199^`, `""`, `BF04199` (uppercase),
`m3-W2-aou-deltas`, `refs/heads/main` → **all REJECTED**.
`bf04199` → **ACCEPTED and GREEN** (non-vacuity: the rejection is not
rejecting everything).

`git_show` is deliberately left unrestricted so the JOB B capture guards can use
symbolic `HEAD` — verified as a separate contract, and the shipped test asserts
`git_show("HEAD", ...) == git_show(<head sha>, ...)`.

---

## 5. THE `actual_text` SEAM CANNOT BE ABUSED FROM PRODUCTION

The **shipped** guard body was driven against forged modules by redirecting its
`_THIS_DIR` at a tmpdir (nothing written into `tests/m3/`):

| Fixture | `grep('actual_text=')` | AST guard |
|---|---|---|
| `actual_text = forged` (spaces) | **False — grep BLIND** | **RED** |
| `**d` where `d = {"actual_text": ...}` | **False — grep BLIND** | **RED** |
| `**{"actual_text": ...}` literal splat | **False — grep BLIND** | **RED** |
| `source_freeze.assert_code_frozen(..., actual_text=1)` (attribute call) | True | **RED** |
| `assert_unchanged_on_disk(..., actual_text=...)` (JOB B seam) | True | **RED** |
| clean call, no seam | False | **GREEN** |
| directory with **zero** guarded calls | False | **RED** (`seen >= 1` non-vacuity fires) |
| **the real `tests/m3/`** | — | **GREEN** |

Three grep-evading shapes caught; the non-vacuity floor is itself demonstrated
to fire. A `grep` would have missed 3 of 5 offenders.

---

## 6. THE PIN HAS EXACTLY ONE SOURCE OF TRUTH

| Check | Result |
|---|---|
| `^R_CODE_REF *=` across `tests/ src/ config/ scripts/ Snakefile` | **1** — `tests/m3/test_source_freeze_pins.py:63` |
| any other `= "bf04199"` binding in `tests/` | only `K3_PRE_FIX_REF` (a deliberate, annotated DIFFERENTIAL SUBSTRATE) |
| `test_finemap_receipt_early_exit.py:86` | `from test_source_freeze_pins import R_CODE_REF as FROZEN_R_CODE_REV` — **imported, not redeclared** |
| `test_qtl_coloc_allele_join.py:137` | `from test_source_freeze_pins import R_CODE_REF as FREEZE_CODE_REF` — **imported, not redeclared** |
| bare `FROZEN_R_REV` / `FREEZE_REF` live consumers | **0** (1 hit, prose only — see ADV-1) |
| `git diff --exit-code` gate on `run_susie_rss.R` anywhere in `tests/` | **0** |

---

## 7. THE BUCKET-ANNOTATION GATE

**Permanent** (`test_every_pin_constant_declares_its_bucket` + a non-vacuity
twin), **currently GREEN**, and **demonstrably capable of failing**.

Live inventory — **16 constants across 12 files, all bucketed**:

| Bucket | Count | Where |
|---|---|---|
| CODE PIN | 2 | `PY_CODE_REF` `bf16289`, `R_CODE_REF` `bf04199` |
| DIFFERENTIAL SUBSTRATE | 14 | 8× `PRE_CHANGE_REF`, `PRE_K1_REF`, `PRE_K1_SMK_REF`, `BASE_COMMIT`, 2× `BASELINE_REV`, `K3_PRE_FIX_REF` |
| HISTORICAL NARRATIVE | 0 | — |

Matches the SUMMARY §5 table exactly.

Synthetic negatives against the shipped gate body:

| Fixture | Gate |
|---|---|
| `X_REF = "abc1234"` unannotated | **RED** |
| plain `# just a note` above it | **RED** |
| annotation naming TWO buckets | **RED** (ambiguity branch) |
| bare `BASE_COMMIT` / bare `BASELINE_REV` | **RED / RED** |
| bucket phrase wrapped across two `#:` lines | GREEN (correctly tolerated) |
| correctly annotated | GREEN |

**The 9 pre-existing modules were annotated comment-only — mechanically
verified:**

| Module | added | non-comment added | deleted |
|---|---|---|---|
| `test_convert_aggregate_target.py` | 3 | **0** | **0** |
| `test_curated_m2_crosswalk_drift.py` | 2 | **0** | **0** |
| `test_finemap_summary_panel_visible.py` | 2 | **0** | **0** |
| `test_ld_allele_aware_join.py` | 2 | **0** | **0** |
| `test_ld_declared_authoritative.py` | 2 | **0** | **0** |
| `test_ld_npz_to_rds_bounded.py` | 2 | **0** | **0** |
| `test_ld_panel_aou_orphan_and_strict.py` | 2 | **0** | **0** |
| `test_ld_read_path_ancestry_gate.py` | 3 | **0** | **0** |
| `test_qtl_coloc_ld_resolution.py` | 2 | **0** | **0** |

Every added line begins with `#:`. Zero deletions anywhere.

---

## 8. DEVIATION D1 — the diagnosis is EXACT and the guard was NOT relaxed

Each leg independently confirmed:

| D1 claim | Verified |
|---|---|
| the plan asserted there is no expected-RED window | **TRUE** — PLAN `:329` "*No task in this plan leaves the tree in an expected-RED state*", restated at T-sr4-13 `:1179` |
| T2 STEP 1's K-3 edit and T2 STEP 4's capture guards land in the **same commit** | **TRUE** — `656529a` contains both the 2 comment-line change to `run_susie_rss.R` and `+2` `git_show("HEAD", SUSIE_R_REL)` guards |
| the guards did not exist at the base | **TRUE** — `git show 1b5b8c6:...` → 0 occurrences |
| ⇒ worktree ≠ HEAD between the edit and the commit ⇒ both guards necessarily fire | **TRUE by construction** |
| "3 ALTERATIONS + 1 = exactly 4 NC-2g tests" | **TRUE** — `ALTERATIONS` has 3 keys; pytest collects **4** `nc2g` tests |
| "4 failed / 182 passed" then "186 passed" | **ARITHMETIC EXACT** — the eight-module set collects **186**; 186 − 4 = 182 |
| **the guard was NOT relaxed** | **TRUE** — AST walk finds **2 bare `assert` nodes**, `real == git_show("HEAD", SUSIE_R_REL)`, neither wrapped in any `Try` or `If`. No skip, no tolerance, no conditional |

The JOB A rewiring is also non-reducing structurally: `_assert_r_freeze_clean`'s
**name and both call sites are byte-identical to the base** (`1b5b8c6`); only the
function body changed, from a `git diff --exit-code` subprocess to
`assert_code_frozen(SUSIE_R_REL, FROZEN_R_CODE_REV, LANG_R)`.

---

## 9. DEVIATION D7 — message-only, confirmed

`5f0520b` touches one file, `+6/−1`:

```
+    # 16 after quick-260806-sr4 (17 before it: ...)   <- 5 comment lines
     assert len(constants) >= 15, (
-        f"the bucket scan found only {len(constants)} revision constants; 17 "
+        f"the bucket scan found only {len(constants)} revision constants; 16 "
```

**The `>= 15` threshold is unchanged.** The single non-comment change is inside
an f-string in the assertion's failure message. No assertion, no threshold, no
control moved.

---

## 10. SKIP INVARIANT

```
$ pytest tests/m3/test_source_freeze.py tests/m3/test_source_freeze_pins.py -rs -q
80 passed in 2.24s
```

**Zero skips, and structurally incapable of skipping:** `grep -c` for
`pytest.skip|@pytest.mark.skip|skipif|importorskip` across all three new files
returns **0 / 0 / 0**; no test in either module takes a fixture other than
`parametrize` arguments. No R subprocess, no Snakemake, no toolchain fixture.

---

## Cross-checks against the orchestrator's findings — NO CONTRADICTIONS

| Orchestrator finding | Verifier re-measurement |
|---|---|
| K-3 closed; `1,909`/`1,900` live, `1,944`/`1,935` gone | `1,944`/`1,935` count = **0**; `1,909`/`1,900` count = **2** ✓ |
| `R_CODE_REF = "bf04199"` — pin did not move | ✓ (and declared exactly once) |
| bytes DIFFER vs `bf04199`, `strip_to_code` IDENTICAL | `bytes identical: False` / `CODE identical: True` ✓ |
| Track A containment | `results/`, `.planning/amendments/`, `src/python/`, `src/scripts/`, `src/snakemake/` paths in diff = **0**; md5 tokens `558fca45`/`462ada6a`/`8255c1ac`/`a041eecc` counts base==head (25/67/67/68) ✓ |
| `DECISIONS.md` 0 deletions | `git diff --numstat` = `136  0` ✓; `DEC-2026-08-06-sr4-freeze-scope` at `:1039` ✓ |
| no whole-file byte gate on the R file survives in `tests/m3` | ✓ |

Also spot-checked: **0** forbidden AoU tokens
(`gsutil|gcloud|bq|dataproc|hailctl`) anywhere in `1b5b8c6..HEAD`.

---

## Working-tree integrity of this verification

Every perturbation ran through the `actual_text=` seam on in-memory strings.
`run_susie_rss.R`'s md5 was captured before and after each of the four verifier
scripts and was **identical every time** (`149c3943f2a980a674777624d4ca7960`).
Nothing was written into `tests/m3/`; the two guard-body experiments used
tmpdirs. The full `tests/m3` suite was deliberately **not** run.

---

## Verdict

**PASSED — 10/10.** The rescope achieves its goal and the new mechanism is
strictly better evidence than the byte pin it replaced: it is comment-free by
demonstration, string-literal-safe against six adversarial concealment shapes,
exhaustively detectable across all 818 code lines, floor-covered over the 700
unfunctioned lines, ref-hardened, seam-hardened against three grep-evading
abuses, single-sourced, and bucket-gated repo-wide — with every one of those
properties **observed failing** on a negative control rather than argued.

Four informational advisories (ADV-1..ADV-4) are recorded in the frontmatter.
None blocks the goal; all are prose or bookkeeping.

---

_Verified: 2026-08-06_
_Verifier: Claude (gsd-verifier) — goal-backward, adversarial_
