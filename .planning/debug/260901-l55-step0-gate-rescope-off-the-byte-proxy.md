# quick-260901-l55 — the STEP 0 gate is rescoped OFF the WHOLE-FILE BYTE PROXY onto a git-ref CODE pin; the parked docstring correction lands; the deferral it was blocking is deleted

**Date:** 2026-09-01 · **Branch:** `m3-W2-aou-deltas` · **Base:** `04a9b2b`
**Nothing was fired.** No enclave, no VM, no Dataproc, no OSF, no `gsutil`, no
`gcloud`, no network contact. The VM was already stopped and stays stopped. **$0.**

---

## 1. The four coupled actions, and why they are coupled

| # | Action | File |
|---|--------|------|
| A1 | Apply the parked docstring patch — the false RETAINED-SET PARITY claim is gone and the ANCHOR-RELATIVE semantics are in its place | `src/python/pairwise_completeness_scan.py` |
| A2 | Rescope the runbook's STEP 0 gate check **(ii)** off `md5sum` + `stat -c '%s'` onto `source_freeze.assert_code_frozen(..., "cb199b6", LANG_PY)`; demote **(iii)** to a FIELD RECORD; rewrite `HOW TO REGENERATE THIS GATE` | `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` |
| A3 | Delete §(1b), the self-invalidating deferral note; keep §(1), which carries the TRUE semantics | `src/python/pcs_panelwide_reclassify.py` |
| A4 | Land the SECONDARY docstring-absence test that the kw8 comment block declared DEFERRED and never built | `tests/m3/test_pairwise_completeness_scan.py` |

They are **mutually invalidating**. Each, alone, makes a committed statement in
another file false or a committed test red:

* **A1 first** turns `test_pending_paste_step0_pins_the_scanner_by_a_CURRENT_content_hash`
  RED (the runbook would carry a stale md5) and turns §(1b)'s own
  self-invalidation RED (it asserts the scanner *still* carries the false
  sentence). Forbidden.
* **A2 first** is GREEN — and it ships a **committed falsehood**. §(1b) states
  that "the live runbook STEP 0 gate pins the scanner's WHOLE-FILE md5 and byte
  size" and names a test that would no longer exist. Nothing would catch it:
  §(1b)'s own test only checked that the md5/size *appear* in the note, and after
  A2 they still appeared — in §(1b), describing a gate that had changed. Shipping
  a known-false sentence to save process is the exact trade the byte-proxy episode
  punished.
* **A3 first** deletes the note while the sentence it corrects is still in the
  scanner — removing the mitigation before the defect.
* **A4 first** is simply RED (the sentence is present).

**There is no ordering that is both green and truthful.** Hence ONE commit. The
*work* was still sequenced (Task 1 → Task 2) so every transition was measured in
the working tree before anything was staged.

---

## 2. The design: a GIT REF, not a hash literal

### Rejected — printing a docstring-insensitive CODE-HASH LITERAL into the runbook

`tests/m3/source_freeze.py`'s module docstring forbids it in terms, verbatim:

> ``ast.unparse`` output can differ across Python minor versions. That is harmless
> **because both sides of every comparison are unparsed by the same interpreter in
> the same process**. Do not "fix" it by freezing an unparse string.

(That quotation is BYTE-EXACT against `tests/m3/source_freeze.py`, checked by
string containment in this session rather than by a committed enforcer — the
first draft of this record and of the runbook both wrote `'fix'` where the
original says `"fix"`, which is a small instance of the same disease this whole
task is about, caught by a self-check and corrected before the amend.)

A literal printed into the runbook **is** a frozen unparse string, and the
enclave's interpreter is not ours. It would also be a fresh instance of
`feedback_fixed_sha_whole_file_pin_is_a_timebomb`: green once, red forever after,
with no cheap remedy.

### Adopted — `assert_code_frozen(SCANNER_REL, SCANNER_CODE_REF, LANG_PY)`

It reads the **working tree** and `git show <ref>:<path>` and unparses BOTH in the
same process, so interpreter drift cancels by construction. The enclave has git
and the repo (STEP 0 already does `git pull --ff-only`), and `cb199b6` is an
ancestor of the run branch.

**The ref is `cb199b6`, and it does NOT move when this plan lands** — M4/M5 below:
the scanner's CODE is identical to `cb199b6` both **before** and **after** the
parked patch, 540 code lines on every side. That is the acceptance demonstration
for the whole rescope: **a prose correction costs nothing.**

`_SHA_RE` inside `assert_code_frozen` refuses a symbolic ref, so the cheapest
possible weakening — re-pointing the gate at `HEAD` — is structurally unavailable.
Observed: SESSION CONTROL B below.

### One wrapped imprecision, wrapped rather than fixed

On failure `assert_code_frozen` appends `source_freeze`'s **generic** re-pin
sentence, which names `PY_CODE_REF in tests/m3/test_source_freeze_pins.py`. That
is the wrong constant and the wrong file for *this* gate. `source_freeze.py` is a
**shared utility** consumed by four other test modules, so it was **not** edited;
instead the runbook's own `except` handler prints an explicit instruction to
**ignore** that clause and names the real constant (`SCANNER_CODE_REF`, in the
block). Observed working in the 1e RED transcript below.

### REUSE (import the shared utility) over an INLINE copy

**Adopted: REUSE.**

1. The property needed is exactly the property that module implements, and its own
   docstring says a hand-rolled stripper "makes a real code change **invisible**,
   which is strictly worse than the byte pin it replaces." The scanner has
   f-strings and `#` inside string literals. `source_freeze`'s Python path uses
   `ast` (comment-insensitivity true *by construction*) and is cross-checked in
   `test_source_freeze.py` against an independent hand-written scanner
   (`_mask_strip_py`), with two synthetic mask invariants (4a/4b) pinned because
   no live file exercises them. A ten-line paste-block copy inherits none of that.
2. `feedback_extract_reusable_utilities` is the standing rule for a recurrent bug
   class. This is the **second** time the byte-proxy class has bitten (2026-08-06,
   2026-08-31). A second copy is precisely what that memory forbids.
3. `_SHA_RE` structurally forbids the cheapest weakening; an inline ten-liner has
   no such guard.

**What breaks under REUSE:** a refactor of `source_freeze.py` (rename, move,
changed signature) breaks the enclave gate. **Bounded and safe** — it fails as an
import error or an assertion, i.e. **STOP**, the safe direction; and the enforcer
test *executes the runbook's own block* at NCSU, so the refactor turns a committed
test RED long before anyone reaches the enclave. `ast.unparse` needs Python ≥ 3.9,
so the block self-checks `sys.version_info` with an explicit STOP rather than
dying on an `AttributeError`.

**What breaks under INLINE:** the copy drifts from the audited stripper
**silently**, and the dangerous direction is *gate green on changed code* —
unbounded, undetectable, and exactly the class that voided the 2026-08-26 sweep.
Restoring safety would require a committed test proving the copy agrees with
`_strip_to_code_py`, which re-creates the dependency **plus** the copy.

**The apparent counter-precedent, argued rather than waved.**
`feedback_freeze_economy_is_not_a_reason_to_take_risk` records that we DECLINED
extracting `ld_allele_join.R` because it would put a *first-of-its-kind runtime
`source()` dependency on the $385–1,084 fire path* while removing duplication that
was **already drift-guarded**. Two material differences here: **(a)** STEP 0 is a
**pre-flight gate**, not the fire path — it runs before anything billable and its
failure mode is **STOP**, the safe direction; **(b)** there is no existing copy and
no drift guard, so here *creating* one is the risk, not removing one.

---

## 3. Measurements

All re-derived on this tree at base `04a9b2b` before being relied on.

| # | Measurement | Result |
|---|-------------|--------|
| M1 | `git apply --check` of the parked patch at HEAD | **PASSES** |
| M2 | scanner md5 / size at HEAD | `e03078ff73502c3c877b0d2ebf93941d` / `73772` |
| M3 | scanner md5 / size WITH the patch applied | `fc1d68dff1f493f6eb57dd427bed638a` / `78843` |
| M4 | `code_lines(scanner, LANG_PY)` at HEAD vs `git show cb199b6:scanner` | **IDENTICAL**, 540 / 540 |
| M5 | `code_lines(PATCHED scanner)` vs the same ref | **IDENTICAL**, 540 — *the patch moves ZERO code* |
| M6 | perturb the CODE anchor `already_occluded=bool(` → `already_occluded_NC=bool(` | `code_lines` **DIFFERS**; first difference at code-line index **187**, naming the `pairs.append(CandidatePair(...))` line; module docstring UNCHANGED |
| M7 | perturb `already_occluded` **inside the module docstring's byte span** | `code_lines` **IDENTICAL**; perturbation non-vacuous; `ast.get_docstring` **CHANGED** |
| M8 | last CODE-moving commit of the scanner | `cb199b6` (quick-260828-uej T1) |
| M9 | the two enforcers the patch NAMES | both **EXIST** (`test_the_already_occluded_rename_is_declined_while_the_sweep_artifact_contract_stands`, `test_already_occluded_is_anchor_relative_and_is_not_the_exclude_side`) |
| M10 | gate slice `_GATE_OPEN`..`_GATE_CLOSE` | lines **61–149** before, **61–225** after; `HOW TO REGENERATE` is INSIDE the slice in both |
| M11 | per-file collect counts at base | scanner **114**, reclassify **21**, source_freeze_pins **39** |
| A1 | module-docstring byte span; `already_occluded` inside it; CODE anchor uniqueness and position | unpatched `[0, 9052]`, 1× in docstring, anchor at offset **27791** (OUTSIDE); patched `[0, 12874]`, 9× in docstring, anchor at offset **32270** (OUTSIDE); `already_occluded=bool(` occurs **exactly once** in BOTH states |
| A2 | lines matching `deletion.pos <` | **3** unpatched (`:468` docstring, `:617` code, `:658` `start_bp <= deletion.pos <= end_bp`), **4** patched (adds `:124`, docstring). Anchor line `:616` unpatched → `:687` patched |

### ⚠ M7 IS A TRAP, AND IT CAUGHT THE PLANNER FIRST

This is the most transferable finding in the whole task. The planner's own first
negative control did

```
text.replace("deletion.pos < partner.pos <= deletion.span_end", PERTURBED, 1)
```

and reported the gate **green** — proving **nothing**, because that phrase's FIRST
occurrence is in the **module docstring**, not the code. A blind `sed` on the same
string is worse still: it matches three lines at HEAD (four after the patch), one
of which yields `deletion.pos <==` → `SyntaxError`, so the operator gets a false
alarm dressed as a finding.

Both controls in the committed test are therefore **AST-scoped by byte range**:
the CODE side anchors on `already_occluded=bool(` (MEASURED unique in both states,
and asserted OUTSIDE the docstring span), and the PROSE side is confined to
`text[DS:DE]`, the docstring's own span. Each asserts non-vacuity **and** that it
landed where it claims — `ast.get_docstring` unchanged on the code side, changed
on the prose side.

This is the **seventeenth** time this repo has been bitten by a pattern matching
text rather than meaning. Three of those were in the 24 hours before this task, by
three different actors (a `text.replace` hitting prose; a `DEFERRAL` grep against a
file saying `DEFERRED`; a process filter matching its own shell).

---

## 4. Negative controls — RED then GREEN, both directions, observed

### 4.1 Task 1e — the ON-DISK session control (gate block, scanner UNPATCHED)

```
STEP 1   md5sum src/python/pairwise_completeness_scan.py
         e03078ff73502c3c877b0d2ebf93941d
         <extracted gate block>  ->  SCANNER CODE PIN ref: cb199b6
                                     CODE PIN PASSED
                                     EXIT=0

STEP 2   anchor line count = 1  ->  LN=616, target line 617
         sed -i "617s/deletion\.pos </deletion.pos <=/" <scanner>

STEP 3   git diff --numstat  ->  1	1	src/python/pairwise_completeness_scan.py
         line 617            ->  deletion.pos <= partner.pos <= deletion.span_end
         md5sum              ->  bc8fa060ce736690e91ac4da15e69a30   (MOVED)
         docstring unchanged ->  True     (so what moved was CODE)
         __pycache__ cleared

STEP 4   <extracted gate block>
         STOP -- the scanner's CODE has MOVED off the STEP 0 pin.
         the CODE of src/python/pairwise_completeness_scan.py (whole file) has MOVED off its pin cb199b6.
         Comments, docstrings, blank lines and trailing whitespace are ignored by this
         comparison, so this is a REAL code change.
         first difference at code-line index 187:
           -   ... already_occluded=bool(deletion.pos < partner.pos <= deletion.span_end) ...
           +   ... already_occluded=bool(deletion.pos <= partner.pos <= deletion.span_end) ...
         (reference: 540 code lines / actual: 540 code lines)
         RE-PIN PROTOCOL: ... PY_CODE_REF in tests/m3/test_source_freeze_pins.py ...
         REMEDY: see HOW TO REGENERATE THIS GATE below. IGNORE the
         'tests/m3/test_source_freeze_pins.py' clause in the message above: that is
         source_freeze's GENERIC re-pin sentence and it does NOT apply to this gate.
         The constant to update is SCANNER_CODE_REF, in this block.
         EXIT=1

STEP 5   git checkout -- <scanner>
         md5sum  ->  e03078ff73502c3c877b0d2ebf93941d   (RESTORED)
         git status --porcelain <scanner>  ->  []       (EMPTY)
         <extracted gate block>  ->  CODE PIN PASSED / EXIT=0
```

**Both directions, both on disk:** RED on a one-character CODE change (above);
GREEN on a docstring-only change — that is Task 2b, the real 89-insertion /
10-deletion patch, below. The wrapper prose about the generic re-pin sentence is
visible doing its job in the STEP 4 transcript.

### 4.2 Task 2b — the ACCEPTANCE DEMONSTRATION (docstring-only change, on disk)

```
git apply .planning/debug/260831-DEFERRED-pairwise-completeness-scan-docstring.patch
APPLIED CLEAN
md5sum   ->  fc1d68dff1f493f6eb57dd427bed638a
stat     ->  78843
numstat  ->  89	10	src/python/pairwise_completeness_scan.py
grep -c 'already visible as ``already_occluded``'  ->  0
<extracted gate block>  ->  SCANNER CODE PIN ref: cb199b6
                            CODE PIN PASSED
                            EXIT=0
```

**5,071 bytes and a moved md5 cost the gate NOTHING.** That is the entire point.

### 4.3 SESSION CONTROLS on the committed ENFORCER TEST (each reverted immediately)

| Control | Perturbation | Result |
|---------|--------------|--------|
| **A** | `SCANNER_CODE_REF` → `1333f3f` (a commit whose scanner CODE differs) | **RED** at check (3): the executed block exits 1; `assert 1 == 0` on the subprocess return code |
| **B** | `SCANNER_CODE_REF` → `HEAD` | **RED** at check (2): *"the STEP 0 code pin 'HEAD' is not an IMMUTABLE revision ... the cheapest possible weakening"* |
| **C** | re-insert `md5: e03078ff…(73772 bytes)` into the gate slice | **RED** at check (5): *"the STEP 0 gate carries a 32-hex content hash again: ['e03078ff73502c3c877b0d2ebf93941d']"* |

After each revert: `114 passed`.

### 4.4 Task 2f — RED-first for the two NEW docstring assertions (4 captures, 2 file states)

| Capture | File state (proved by md5/size) | Assertion | Result |
|---------|-------------------------------|-----------|--------|
| 1 | REVERTED — `e03078ff…` / `73772`, `git status` empty | `test_the_scanner_docstring_no_longer_claims_already_occluded_is_the_exclude_side` | **RED** at the `"already visible as ``already_occluded``" not in flat` assertion |
| 2 | same | `test_the_tool_and_the_scanner_agree_that_already_occluded_is_anchor_relative` claim (3) | **RED** at the `_SCANNER_FALSE_CLAIM not in scanner_flat` assertion |
| 3 | RE-APPLIED — `fc1d68df…` / `78843` | capture-1's test | **GREEN** |
| 4 | same | capture-2's test | **GREEN** |

`__pycache__` was cleared at every transition. The byte lengths differ (73772 vs
78843) so the `.pyc` `(mtime, size)` validation could not have masked either
transition anyway — but
`feedback_negative_control_defeated_by_bytecode_cache` is not negotiated with.

**Bonus observation at capture 1/2:** with the scanner REVERTED, the rescoped CODE
PIN enforcer was still **GREEN** (`1 passed`). The gate is indifferent to which of
the two prose states the scanner is in — which is the property, stated as an
observation rather than a claim.

### 4.5 One residual, recorded rather than omitted

Check (3) of the enforcer executes the runbook block by subprocess and asserts
exit 0 — a GREEN assertion. Its RED counterpart cannot be *committed* without
writing the working tree (`assert_code_frozen`'s `actual_text` seam is banned in
every `tests/m3/` module but `test_source_freeze.py`, by an AST walk). The RED is
covered **in memory** by control (4a) in the same test, **on disk** by the 1e
session control, and **at the test level** by SESSION CONTROL A above. Bounded and
stated.

---

## 5. The byte-proxy episode — CLOSED as a REPEAT

`feedback_scope_a_guard_to_the_property_not_a_proxy` was baked **2026-08-06** from
`run_susie_rss.R`, where `git diff --exit-code <SHA> -- <file>` made shipping a
known-false census figure (`1,944`, correct `1,909`) **cheaper** than correcting
the comment that carried it.

**Repeated 2026-08-31.** We designed the STEP 0 gate ourselves in `quick-260828-uej`
T3 — as the remedy for a gate that matched a commit *subject* — and chose
whole-file md5 + byte size as its content pin. Under four weeks later it was
blocking deletion of a **known falsehood** at `pairwise_completeness_scan.py:122`,
and the escape route it left open was to leave the falsehood in place. A rule that
makes shipping a falsehood cheaper than fixing it is mis-scoped, twice.

**What replaced it:** a CODE pin against an immutable git ref, comment- and
docstring-insensitive *by construction* (`ast`, not a regex).

**The named enforcer that fails if it regresses:**
`tests/m3/test_pairwise_completeness_scan.py::test_pending_paste_step0_pins_the_scanner_CODE_against_a_git_ref`
— check (5) fails on any 32-hex token or the scanner's current byte size
reappearing anywhere in the gate slice. Observed RED (SESSION CONTROL C).

**The generalisation:** when the correct action becomes the expensive one, that is
a scoping bug report about the guard, not a reason to take the cheap action.

---

## 6. What did NOT change

**No pre-registered or measured number moved.**

| Quantity | Value | Status |
|----------|-------|--------|
| `wc -l` / POOLED candidate rows | 353090 / 353089 | untouched |
| undefined rows / distinct pairs | 15 / 13 | untouched |
| already-occluded split | 10 / 3 | untouched |
| offset histogram | `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}` | untouched |
| panel-wide reclassification | 12 of 13 pairs, 14 of 15 rows never reach the matrix; **1** survivor (`m2_region_00149`, offset −1) | untouched |
| partial-confounding tail | 3,094 rows / 0.876% | untouched |

Proof: `git diff --stat` over `.planning/amendments/`,
`src/python/occlusion_span_filter.py`, `src/python/run_native_ld_panel.py`,
`src/python/fire_verifier.py`, `src/python/aou_ld_panel.py` is **EMPTY**. The
runbook's `--ancestry` token count is still **0**. Capability check (iv) and the
`WHAT EACH FAILURE MEANS` block are byte-verbatim (`276` / `552` /
`manifest windows: 276 distinct region ids: 276` / `CAPABILITY CHECK PASSED` all
still assert green).

---

## 7. Deviations from the plan, with the measurement that justified each

**D-1 — §(1) did not actually carry the token `PANEL-WIDE`.** Rule 1 (auto-fix).
The plan's replacement test asserts that `pcs_panelwide_reclassify`'s §(1) states
`ANCHOR-RELATIVE` **and** `PANEL-WIDE`. MEASURED immediately after deleting §(1b):
`ANCHOR-RELATIVE` True, **`PANEL-WIDE` False** — the uppercase token lived only in
the deleted §(1b); §(1) said "panel-wide" in lower case once, in a trailing
sentence. Two options: weaken the assertion, or make §(1) carry the contrast.
Chose the latter — §(1) is now the *only* place in this module carrying the
correction, so it should state the ANCHOR-RELATIVE vs PANEL-WIDE contrast in the
register the deleted note had, and it now also names the runtime enforcer that
demonstrates the disagreement. Weakening the assertion to a case-insensitive match
would have been fixing the thermometer.

**D-2 — three stale line-number citations, created by this task.** Rule 1
(auto-fix). The patch moves `already_occluded=bool(` from `:616` to `:687`, which
silently falsified:
* `src/python/pcs_panelwide_reclassify.py:6` — "computed at `…:616`"
* `tests/m3/test_pcs_panelwide_reclassify.py:7` — "ONLY (`…:616`)"
* `tests/m3/test_pairwise_completeness_scan.py` banner — "the RETAINED-SET PARITY
  bullet (`:122`)"

Rather than re-transcribe `:687` — a proxy that decays again on the next edit
above it — the two surviving citations now name the **symbol**
(`pairwise_completeness_scan.enumerate_candidates`), which is strictly stronger
and cannot rot silently. The third was inside the banner this task rewrote whole.
This is the same scoping lesson applied to a citation.

---

## 8. Suite

Baseline `1167 passed / 33 skipped / 0 failed`, 1200 collected.
Result and the BY-NAME reconciliation are recorded in
`.planning/quick/260901-l55-the-three-coupled-post-sweep-actions-app/260901-l55-SUMMARY.md`.
