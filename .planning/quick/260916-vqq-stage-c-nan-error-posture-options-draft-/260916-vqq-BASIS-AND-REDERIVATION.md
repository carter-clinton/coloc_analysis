# quick-260916-vqq — BASIS capture, v1→BASIS re-derivation of all 88 citations, and the new-fact measurements for draft v2

**Task 1 of 4. This file MEASURES; it authors nothing.** Every number below was produced in this task
at the BASIS commit named in §1. Nothing was copied forward from the plan's
`<measured_at_planning_time>` block, from the revision brief, or from `260916-kht-verify.py`'s
constants. Where a measurement disagrees with any of those, the disagreement is stated as a FINDING.

---

## 1. BASIS

| field | value |
|---|---|
| BASIS (full) | `74f962d21b07a8b765dfba6c3825448e05eb17e7` |
| BASIS (short) | `74f962d` |
| subject | `docs(quick-260916-vqp): close out — PLAN + SUMMARY + VERIFICATION (5/7, both gaps CLOSED here) + STATE ledger; fix the two self-inflicted stale citations` |
| branch | `m3-W2-aou-deltas` |
| tracked tree at capture | `git status --porcelain --untracked-files=no` → EMPTY |

From here on BASIS is the only basis. `HEAD` is never cited in v2.

### 1a. vqp ordering gate (pre-flight d) — PASSED

`git log --format='%H %s' | grep -E '^[0-9a-f]{40} docs\(quick-260916-vqp\)'` yields **4** lines; the
newest is:

```
74f962d21b07a8b765dfba6c3825448e05eb17e7 docs(quick-260916-vqp): close out — PLAN + SUMMARY + VERIFICATION (5/7, both gaps CLOSED here) + STATE ledger; fix the two self-inflicted stale citations
3f418df74ac1701f71336b26b8a887bf8b6a6ca9 docs(quick-260916-vqp): refresh the two resume surfaces — HANDOFF.json B1 fields …
5a2b437c91678020a96c1b75a6b5d69b7773468d docs(quick-260916-vqp): insertion-only history records — .continue-here 2026-09-16 block, halt-record ⚠ SUPERSEDED …
f8f30e3af2b570bea835290e0c87b483e27991ea docs(quick-260916-vqp): bank the 2026-09-16 blast-radius review (byte-identical, as-received) …
```

`git merge-base --is-ancestor 74f962d21b07a8b765dfba6c3825448e05eb17e7 HEAD` → rc 0. The newest vqp
commit **IS** BASIS (vqp's close-out is HEAD), so it is trivially an ancestor of BASIS as well.

⚠ The orchestrator's note said to capture BASIS myself and not assume `621701c`. Measured: BASIS is
`74f962d`, **four commits after** `621701c`. Every number in the plan's `<measured_at_planning_time>`
block was taken at `621701c`, i.e. BEFORE vqp — which is why §3's OD deltas are `+35`, not `0`.

### 1b. Immutability at pre-flight (size THEN md5) — PASSED, figures reproduce exactly

| file | declared size | measured size | declared lines | measured lines | declared md5 | measured md5 |
|---|---|---|---|---|---|---|
| `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` (v1) | 18,309 B | **18,309 B** | 223 | **223** | `763f412bb1a8dbdb38f2cc332ed5a21d` | **`763f412bb1a8dbdb38f2cc332ed5a21d`** |
| `.planning/quick/260916-kht-bank-…/260916-kht-verify.py` | 88,899 B | **88,899 B** | 1,711 | **1,711** | `50a4de7a954db77a6f162b9dcb573504` | **`50a4de7a954db77a6f162b9dcb573504`** |

`git diff --quiet HEAD -- <both>` → rc 0. No disagreement to report.

### 1c. kht positive control (pre-flight f) — PASSED, verbatim

```
RESULT GREEN checks=317 parsed=88 table=88 verified=88
```

(rc 0, default mode.)

### 1d. Halt-record annotation gate (pre-flight g / A-6 iv) — PASSED

Keyed on the ASCII `SUPERSEDED 2026-09-16` (no glyph), matching vqp's own enforcer. **1 hit:**

```
256:## ⚠ SUPERSEDED 2026-09-16 — RAM-1's DIAGNOSIS held; its PRESCRIBED FIX is falsified
```

**The halt record is insert-only between `c93e97b` and BASIS.** Measured: 252 lines at `c93e97b`,
301 at BASIS, and `old == new[:252]` is **True** — the +49 lines are appended at the end, so the
annotation does **not** shift the falsified passages. The plan anticipated a shift; there is none.
This is a FINDING relative to the plan's orientation (it said the annotation "may SHIFT these line
numbers"), and it is why every `c-halt:` anchor below is still re-located by content anyway.

#### The falsified ranges at BASIS, located by UNIQUE content anchors (A-4)

Every anchor is matched under `norm()` and its hit count asserted **== 1** before use:

| anchor | text (verbatim) | hits | line |
|---|---|---|---|
| `H1-start` | ``**RAM-1 — `peak_ram_gib` is NOT a per-region measurement (CONFIRMED defect).**`` | **1** | 112 |
| `H1-meas` | `(inherited; a 2,854-variant region cannot use 26.6 GiB)` | **1** | 119 |
| `H1-end` | ``Clean fix: `subprocess.Popen` + `os.wait4(pid, 0)`, whose `rusage` is that child's own.`` | **1** | 124 |
| `H2` | `4. Separately and independently: **RAM-1** fix (TDD) and the **00071** anchor.` | **1** | 146 |

**Rejected anchors, measured (A-4):**

| rejected anchor | hits | lines | why rejected |
|---|---|---|---|
| bare `RAM-1` | **5** | 112, 146, 256, 293, 294 | ambiguous — 112 is NOT falsified, 146 is |
| `Clean fix:` | **2** | 124, 280 | the SUPERSEDED annotation re-quotes it at 280 |
| `RAM-1 fix (TDD)` (the plan's prose anchor) | **0** | — | does not occur literally; the file has `**RAM-1** fix (TDD)` |

**Forbidden ranges (`c-halt:`), derived from the unique anchors:**

- **F1 = `:118-125`** — `H1-meas`(119) − 1 through `H1-end`(124) + 1: the `ru_maxrss`-inheritance
  measurement through the `Popen` + `os.wait4` prescription and its continuation line.
- **F2 = `:146-146`** — `H2`(146).

Cross-check against vqp's own annotation text, which names `:118`-`:122` and `:124` and `:146`:
F1 ∪ F2 is a **superset** of what vqp marks. Agreed.

**v1's five citations into that file** are `:11-16`, `:20-21`, `:45-58`, `:104-107`, `:150-179`.
Measured: **none intersects F1 or F2** (`150 > 146`). `c-halt:` is therefore cheap — but it is a gate,
not an assumption.

---

## 2. Which cited files moved at all (measured before the per-claim work)

`git diff --numstat c93e97b 74f962d…` over all 13 `PATHS` entries:

```
49	0	.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md
35	0	.planning/osf_deviations.md
156	13	src/python/run_native_ld_panel.py
```

Every other cited file (`AP RF FV PL DI MK TR U7 TFV`) is **byte-unchanged** `c93e97b`..BASIS.
`run_native_ld_panel.py` is net **+143** (156 − 13). This is context for §3 — it is **not** the
method used there.

---

## 3. The v1 → BASIS re-derivation of all 88 CLAIMS rows

**Method (re-location, never offset).** For each of the 88 positional CLAIMS rows in
`260916-kht-verify.py` (ids `c01..c81`, `n01..n07`), in the reading order the draft parses:

1. The v1 range is the range the citation token actually resolves to in v1 (parsed with the kht
   `CITE` regex, `parse_key` / `keymap_of` / `resolve` bare-ref inheritance) — not a range copied
   from a comment.
2. The cited file's text **at `c93e97b`** over that range is taken as a search key. The key is grown
   with symmetric context (0, 1, 2, 3, 5, 8, 12, 20 lines) until the **exact line block** occurs
   **exactly once** in the same file **at BASIS**. The BASIS range is read back off that unique hit.
3. The row's payload is then re-checked at the BASIS range with the same `norm()` / `seg_in()` /
   `match_payload` semantics the kht checker uses (`kind="Q"` → `…`-separated segments in order;
   `kind="T"` → normalized substrings; NOT-tokens must be absent; MK rows checked at BOTH the repo
   range and the posted `P` range).

Verdicts: **HOLDS** = the v1 range is still correct; **MOVED** = payload found, at a different range;
**FALSE** = payload not found at BASIS, or found only ambiguously.

**Result: 58 HOLDS, 30 MOVED, 0 FALSE.**

⚠ **A method note that is itself a finding.** A first pass located each payload by sliding a window
and breaking ties on the smallest `|delta|`. That pass got **c09** and **c66** WRONG (it returned
`:1148 → :1109` and `:967 → :958`, i.e. *negative* deltas) because both payloads are one-line and
generic (`append_panel_row(` / `return result`) and occur at 4–5 places in the file. Minimal-|delta|
is not a re-location rule; it is a proximity prior. The context-grown exact-block method above has no
tie to break, and returns `+143` for both, consistent with their neighbours `c49` (`:1144-1148 →
:1287-1291`) and `c51`. Recorded because the wrong answer was *plausible* and self-consistent.

| claim | file | v1 range | BASIS range | delta | verdict |
|---|---|---|---|---|---|
| `c01` | AP | 398-398 | 398-398 | 0 | **HOLDS** |
| `c02` | AP | 372-373 | 372-373 | 0 | **HOLDS** |
| `c03` | AP | 417-417 | 417-417 | 0 | **HOLDS** |
| `c04` | RF | 360-366 | 360-366 | 0 | **HOLDS** |
| `c05` | RN | 1325-1328 | 1468-1471 | +143 | **MOVED** |
| `c06` | PL | 218-228 | 218-228 | 0 | **HOLDS** |
| `c07` | RN | 1090-1093 | 1233-1236 | +143 | **MOVED** |
| `c08` | RN | 1144-1146 | 1287-1289 | +143 | **MOVED** |
| `c09` | RN | 1148-1148 | 1291-1291 | +143 | **MOVED** |
| `c10` | RN | 1101-1107 | 1244-1250 | +143 | **MOVED** |
| `c11` | RN | 1278-1279 | 1421-1422 | +143 | **MOVED** |
| `c12` | FV | 1097-1099 | 1097-1099 | 0 | **HOLDS** |
| `c13` | FV | 302-303 | 302-303 | 0 | **HOLDS** |
| `c14` | FV | 324-326 | 324-326 | 0 | **HOLDS** |
| `c15` | FV | 381-389 | 381-389 | 0 | **HOLDS** |
| `c16` | FV | 976-981 | 976-981 | 0 | **HOLDS** |
| `c17` | AP | 55-61 | 55-61 | 0 | **HOLDS** |
| `c18` | AP | 422-423 | 422-423 | 0 | **HOLDS** |
| `c19` | FV | 999-1001 | 999-1001 | 0 | **HOLDS** |
| `c20` | RN | 1278-1278 | 1421-1421 | +143 | **MOVED** |
| `c21` | RN | 806-815 | 949-958 | +143 | **MOVED** |
| `c22` | HA | 20-21 | 20-21 | 0 | **HOLDS** |
| `c23` | RN | 1325-1328 | 1468-1471 | +143 | **MOVED** |
| `c24` | HA | 11-16 | 11-16 | 0 | **HOLDS** |
| `c25` | OD | 657-663 | 692-698 | +35 | **MOVED** |
| `c26` | TR | 39-39 | 39-39 | 0 | **HOLDS** |
| `c27` | MK | 488-489 | 488-489 | 0 | **HOLDS** |
| `c28` | TR | 29-29 | 29-29 | 0 | **HOLDS** |
| `c29` | MK | 428-428 | 428-428 | 0 | **HOLDS** |
| `c30` | MK | 478-479 | 478-479 | 0 | **HOLDS** |
| `c31` | TR | 47-47 | 47-47 | 0 | **HOLDS** |
| `c32` | MK | 483-485 | 483-485 | 0 | **HOLDS** |
| `c33` | MK | 322-325 | 322-325 | 0 | **HOLDS** |
| `c34` | TR | 43-43 | 43-43 | 0 | **HOLDS** |
| `c35` | TR | 45-45 | 45-45 | 0 | **HOLDS** |
| `c36` | TR | 49-49 | 49-49 | 0 | **HOLDS** |
| `c37` | TR | 53-53 | 53-53 | 0 | **HOLDS** |
| `c38` | MK | 490-491 | 490-491 | 0 | **HOLDS** |
| `c39` | TR | 59-59 | 59-59 | 0 | **HOLDS** |
| `c40` | MK | 414-417 | 414-417 | 0 | **HOLDS** |
| `c41` | TR | 25-25 | 25-25 | 0 | **HOLDS** |
| `c42` | MK | 474-475 | 474-475 | 0 | **HOLDS** |
| `c43` | TR | 49-49 | 49-49 | 0 | **HOLDS** |
| `c44` | MK | 469-472 | 469-472 | 0 | **HOLDS** |
| `c45` | PL | 213-228 | 213-228 | 0 | **HOLDS** |
| `c46` | HA | 45-58 | 45-58 | 0 | **HOLDS** |
| `c47` | RN | 1068-1069 | 1211-1212 | +143 | **MOVED** |
| `c48` | RN | 1090-1090 | 1233-1233 | +143 | **MOVED** |
| `c49` | RN | 1144-1148 | 1287-1291 | +143 | **MOVED** |
| `c50` | RN | 1101-1107 | 1244-1250 | +143 | **MOVED** |
| `c51` | RN | 1149-1154 | 1292-1297 | +143 | **MOVED** |
| `c52` | RN | 723-725 | 866-868 | +143 | **MOVED** |
| `n01` | RN | 806-815 | 949-958 | +143 | **MOVED** |
| `n07` | RN | 866-872 | 1009-1015 | +143 | **MOVED** |
| `c53` | RN | 923-939 | 1066-1082 | +143 | **MOVED** |
| `c54` | RN | 961-965 | 1104-1108 | +143 | **MOVED** |
| `c55` | RN | 1129-1139 | 1272-1282 | +143 | **MOVED** |
| `c56` | RN | 799-815 | 942-958 | +143 | **MOVED** |
| `c57` | FV | 330-399 | 330-399 | 0 | **HOLDS** |
| `c58` | FV | 309-312 | 309-312 | 0 | **HOLDS** |
| `c59` | RN | 866-872 | 1009-1015 | +143 | **MOVED** |
| `c60` | DI | 1148-1191 | 1148-1191 | 0 | **HOLDS** |
| `c61` | FV | 875-939 | 875-939 | 0 | **HOLDS** |
| `c62` | RF | 360-366 | 360-366 | 0 | **HOLDS** |
| `c63` | AP | 424-428 | 424-428 | 0 | **HOLDS** |
| `c64` | TR | 43-43 | 43-43 | 0 | **HOLDS** |
| `c65` | TR | 45-45 | 45-45 | 0 | **HOLDS** |
| `c66` | RN | 967-967 | 1110-1110 | +143 | **MOVED** |
| `c67` | RN | 1090-1090 | 1233-1233 | +143 | **MOVED** |
| `c68` | TR | 53-53 | 53-53 | 0 | **HOLDS** |
| `n02` | AP | 393-393 | 393-393 | 0 | **HOLDS** |
| `c69` | FV | 363-370 | 363-370 | 0 | **HOLDS** |
| `c70` | OD | 703-704 | 738-739 | +35 | **MOVED** |
| `c71` | MK | 467-469 | 467-469 | 0 | **HOLDS** |
| `c72` | MK | 483-483 | 483-483 | 0 | **HOLDS** |
| `c73` | FV | 335-336 | 335-336 | 0 | **HOLDS** |
| `c74` | HA | 150-179 | 150-179 | 0 | **HOLDS** |
| `c75` | HA | 104-107 | 104-107 | 0 | **HOLDS** |
| `n03` | OD | 660-663 | 695-698 | +35 | **MOVED** |
| `n04` | MK | 255-256 | 255-256 | 0 | **HOLDS** |
| `n05` | MK | 255-256 | 255-256 | 0 | **HOLDS** |
| `c76` | OD | 685-689 | 720-724 | +35 | **MOVED** |
| `c77` | OD | 682-682 | 717-717 | +35 | **MOVED** |
| `c78` | OD | 670-671 | 705-706 | +35 | **MOVED** |
| `c79` | MK | 414-417 | 414-417 | 0 | **HOLDS** |
| `n06` | RF | 369-370 | 369-370 | 0 | **HOLDS** |
| `c80` | MK | 483-483 | 483-483 | 0 | **HOLDS** |
| `c81` | MK | 414-417 | 414-417 | 0 | **HOLDS** |

### 3a. Are the deltas uniform per file? (measured, not assumed)

| file key | path | distinct deltas observed | rows |
|---|---|---|---|
| `AP` | `260812-ox1-AGENT-PROMPT.md` | `{0}` | 6 |
| `RF` | `260812-ox1-READY-TO-FIRE.md` | `{0}` | 3 |
| `RN` | `src/python/run_native_ld_panel.py` | `{+143}` | 24 |
| `FV` | `src/python/fire_verifier.py` | `{0}` | 12 |
| `PL` | `src/python/plink_ld_to_npz.py` | `{0}` | 2 |
| `OD` | `.planning/osf_deviations.md` | `{+35}` | 6 |
| `HA` | `260824-STAGE-B-HALT-…md` | `{0}` | 5 |
| `DI` | `deferred-items.md` | `{0}` | 1 |
| `MK` | mk7ze (posted) | `{0}` | 21 |
| `TR` | trsx5 (posted) | `{0}` | 8 |

**Measured observation:** the deltas ARE uniform within every file — `RN` +143 on all 24 rows, `OD`
+35 on all 6, everything else 0. There is **no non-uniformity anywhere**. That is a measured
coincidence of where the insertions landed (`RN`'s hunks are all above the lowest RN citation; `OD`'s
+35 is appended above `:567`'s entry body… see the FINDING below), **not a rule**, and it was
established per-claim rather than assumed.

⚠ **FINDING vs the plan's orientation.** `<measured_at_planning_time>` predicted `RN` +143 (correct)
but was written before vqp; it did not predict `OD` at all. The orchestrator's hand-off note predicted
the `OD` shift as `:657→:692, :660→:695, :670→:705, :685→:720, :703→:738`. **All five reproduce
exactly** (c25 657→692, n03 660→695, c78 670→705, c76 685→720, c70 703→738), and the sixth OD row
`c77` (`:682 → :717`) is likewise +35.

### 3b. The MOVED/FALSE verdict set (a deliverable, as a SET of ids)

30 ids, sorted:

```
c05 c07 c08 c09 c10 c11 c20 c21 c23 c25 c47 c48 c49 c50 c51 c52 c53 c54 c55 c56
c59 c66 c67 c70 c76 c77 c78 n01 n03 n07
```

Composition: **24 `RN` rows** (all at +143) + **6 `OD` rows** (all at +35). **0 FALSE.**
Task 2a's `--baseline` must reproduce exactly this set mechanically, reconciled by SET EQUALITY
(symmetric difference empty and printed), not by count — two opposite-sign component errors cancel in
a count and survive it.

---

## 4. The kht checker's other anchors, re-derived at BASIS

### 4a. AST anchors S1–S9

| anchor | what kht asserts | status at BASIS | measured |
|---|---|---|---|
| `S1`/`S2` | innermost `def` containing `RN:1144` is `process_region` | ⚠ **GREEN FOR THE WRONG REASON** | at `c93e97b` `:1144` is `except Exception as e:  # one bad region never aborts the whole loop`; at BASIS `:1144` is `# would race under any future sharded fan-out). Fresh path` — a different, unrelated line that happens to be inside the SAME long function, so `innermost == process_region` still holds |
| `S3` | `RN:967` inside `if fired:` | **STALE** | at BASIS `:967` is `}` (a dict-literal close); the real statement is at `:1110` |
| `S4` | `RN:962-965` inside `if fired:` | **STALE** | at BASIS `:962` is `"region_id": region_id, "chr": chrom, "n_var": None,`; the real block is `:1105-1108` |
| `S5` | `RN:1106` inside `if ok:` | **STALE** | at BASIS `:1106` is the argument line `gate_sidecar,`; the real statement is `:1249` |
| `S6` | `RN:1136-1139` inside `if ok:` | **STALE** | at BASIS `:1136` is a comment `# semantics are unchanged.`; the real block is `:1279-1282` |
| `S7`/`S8`/`S9` | `max_n_var` literal, the excludelist/sidecar structure, the AST-located `gate_sidecar = …` | **hold in substance** | S9 is already AST-anchored on the `gate_sidecar` assignment rather than a line number, which is why it survives the shift |

**Consequence for the v2 checker (this is the whole S2 lesson).** A line number that merely *falls
inside* a long function is not an anchor — `process_region` spans hundreds of lines, so `S2` cannot
distinguish "the right statement" from "any line in the function". **Every `c-ast:` check in
`260916-vqq-verify.py` is anchored on an AST-located symbol or statement identity** (a `FunctionDef`
by name, a `Raise` by its message constant, an assignment target, `If`-body containment by node
range), never on a bare line number.

### 4b. `c-hand` inputs

| id | input | measured at BASIS |
|---|---|---|
| H1 | 1 of 21 sampled regions scaled to 276 | `276 × 1/21 = 13.1429…` → **≈13**; Clopper-Pearson exact 95% for x=1, n=21 = `0.001205 … 0.238160`, ×276 = **0.33 … 65.73** → v1's printed "0.3–66" **reproduces** |
| H2 | STATE.md frontmatter marker + runtime | marker `PRIOR: 2026-09-01 — ✅ SWEEP COMPLETE` present in the `last_activity` field (line **18** at BASIS); the same field carries **`Runtime 48m not 4h20m`** |
| H3 | the `## 2026-09-03 —` OD entry start, found by HEADING SEARCH | **`:567`** at BASIS (was `:532`; +35). Full heading: `## 2026-09-03 — AFR native-panel DEFINED-ROW TAIL disclosure (measured characterisation; NO amendment, NO predicate change, NO carrier floor)` |
| H4 | U7 md5 ≠ trsx5 md5 (the repo draft is not the posted body) | U7 and TR are byte-unchanged `c93e97b`..BASIS; their md5s differ (TR = `c19be8b2ad7cd6a45fee1d668d8a9cf9`, 9,695 B) |
| H5 | the basis statement | v1 says `Code at HEAD c93e97b`; v2 states BASIS `74f962d21b07a8b765dfba6c3825448e05eb17e7` |
| — | X2 scratch size | `120,000² × 4 B = 57,600,000,000 B = 57.6 GB` — v1's figure **reproduces** |
| — | v1's Option-D scaling | `48 min × 276/21 = 630.86 min = 10.51 h` — v1's "~10.5 h" **reproduces** (but see §5 N5: the instrument attribution is the problem, not the arithmetic) |

⚠ **trsx5 line-count trap, re-confirmed.** `wc -l` prints **58**; `str.splitlines()` gives **59**
(no trailing newline). All trsx5 line numbers below are `splitlines()` 1-based.

### 4c. The `d:` sweep, recomputed

Both posted bodies normalized (markdown stripped, whitespace collapsed, lower-cased) and searched:

| term | mk7ze (posted P1–P333) | trsx5 (posted) |
|---|---|---|
| `halt` | **0** | **0** |
| `abort` | **0** | **0** |
| `skip` | **0** | **0** |
| `partial` | **0** | **0** |
| `incomplete` | **0** | **0** |
| `feasib` | **0** | **0** |
| `defer` (control) | **17** | **4** |
| `raise` (control) | **3** | **2** |
| `deferred_infeasible_square` (raw) | **0** | **0** |
| `deferredinfeasiblesquare` (underscore-stripped — `norm()` strips `_`) | **0** | **0** |

Every figure v1 printed **reproduces exactly**. The underscore-stripped form matters because `norm()`
deletes `_`, so a raw-only search would be a green-over-nothing check.

### 4d. The `e:` git-freeze property, RE-DERIVED (kht's `SINCE` is now FALSE)

⚠ **FINDING.** `260916-kht-verify.py` pins `SINCE = "2026-08-24 00:00:00 -0400"` and asserts the log
of `src/python/{run_native_ld_panel,fire_verifier,plink_ld_to_npz}.py` since then is EMPTY. At BASIS
that window contains **1** commit, so the constant is false. Re-derived:

| quantity | measured at BASIS |
|---|---|
| newest commit touching the three files | `9a3eb9786e20208249d04f5510f5d3799af8ec4c`, **2026-09-16 19:17:15 -0400** (`fix(quick-260916-ocb): _run_plink reports plink's OWN peak RSS via a small isolated launcher + os.wait4 (RAM-1 …)`) |
| `SINCE` that yields 0 commits | **`2026-09-17 00:00:00 -0400`** → **0** |
| `SINCE_CONTROL` that yields ≥ 1 | **`2026-08-01 00:00:00 -0400`** → **7** (non-empty; an empty control proves nothing) |
| kht's `SINCE = 2026-08-24` | **1** commit → the old constant no longer expresses "frozen" |

The v2 checker uses the re-derived pair. It does **not** inherit `2026-08-24`.

---

## 5. N1–N9 — the new facts v2 needs (each with its BASIS file:line and a verbatim quote)

### N1 — the RETAINED fully-NaN-row → drop rule

- **trsx5:37** (located by `splitlines()`, 59 lines total), verbatim:

  > The fully-NaN-row → drop rule (prior item (a) first branch): a variant row that is entirely NaN (a zero-variance / monomorphic-within-analysis-set source) is dropped by MAF / missingness QC. This converges with the new exclude policy and is retained.

- **mk7ze P321 / R488**, located by verbatim search (not by subtracting 167 by hand), verbatim:

  > - **The fully-NaN-row → drop rule** and **the raw-panel NaN-raise contract** (the raw

  and its continuation **P322 / R489**:

  > per-region `.npz` reader continues to RAISE on any NaN rather than silently coercing it).

  **Measured: the drop rule is named on P321 / R488 alone** (P322 carries only the NaN-raise
  contract's parenthetical). `P + 167 = R` holds for both (321+167=488, 322+167=489).

This is the **only posted rule that disposes of NaN-bearing variants**, and v1 has no §1 row for it.
It becomes v2's **T9** (appended; T1–T8 are NOT renumbered).

### N2 — what the fence actually scopes

- **trsx5:49**, verbatim:

  > All three outcomes are reportable; excluding variants silently (without a manifest), fabricating a correlation value, or choosing the occlusion criterion to obtain a particular fine-mapping result are the only paths not on this list.

- **mk7ze P302-305 / R469-472**, verbatim:

  > variant. UNTOUCHED. The 2026-07-10 record fences *"choosing the occlusion criterion to
  > obtain a particular fine-mapping result"*; the anomaly GATE is a different object from the
  > CRITERION, and recalibrating the gate against a measured population is not that prohibited
  > act. The criterion is not modified here in any way.

**Measured scope:** what is fenced is *choosing* the criterion **to obtain a particular fine-mapping
result**. mk7ze explicitly separates recalibrating the GATE from that prohibited act. v1's Option E
says "The criterion is unchanged and fenced (T8)" — measured, the posted text fences a *motive*, not
any change whatsoever, so whether a change **for a stated methodological reason** is the fenced act is
an open question. (R5 ii.)

### N3 — DRAFTED — NOT POSTED, and the entry's extent

| item | BASIS line |
|---|---|
| entry heading `## 2026-09-03 — AFR native-panel DEFINED-ROW TAIL disclosure …` | **567** |
| `- **Status:** DRAFTED — NOT POSTED; placement and posting are Carter's. No agent has contacted` | **569** |
| next `## ` heading after 567 | **none** — the entry runs to EOF |
| file length at BASIS | **1,057** lines (was 1,022 at `621701c`) |

So the entry's extent is **`:567`–`:1057`**, and **every OD citation v2 carries falls inside it**:
`:692-698` (c25), `:695-698` (n03), `:705-706` (c78), `:717` (c77), `:720-724` (c76), `:738-739` (c70).
All ≥ 567 and ≤ 1057. ✔

### N4 — the C-rate one-sided caveat

`.planning/osf_deviations.md:714-717` at BASIS, verbatim:

> (`.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md:62-70`), and the
> pre-committed 21-region sample does not contain it. Our own `.planning/STATE.md:287` had already
> concluded that the residual class **sits immediately adjacent to the REF span on EITHER side**
> and that this sweep could observe only one side. **Production tests the rate on BOTH sides.**

The two phrases the plan names — `this sweep could observe only one side` and
`**Production tests the rate on BOTH sides.**` — are on the **same line, `:717`** (which is also
`c77`'s BASIS range).

### N5 — Option D's real deliverable ⚠ THE BRIEF'S RUNTIME IS WRONG

**(i) The pairwise-completeness scan alone is ANCHOR-RELATIVE.** Its `already_occluded` column is
computed relative to the anchor deletion, not against the `--exclude` side, so the scan by itself does
not answer "does the pair reach the matrix". The purpose-built record is
`.planning/debug/260831-seth-brief-blind-review-already-occluded-is-anchor-relative.md` (325 lines at
BASIS); **`:50-53`** verbatim:

> So `already_occluded == False` means **"not inside THIS anchor's span"**. It does
> **not** mean "survives `--exclude`", and **`n_undefined_not_already_occluded`
> does not count pairs that survive filtering.** The two predicates are different
> questions, and the field answers the smaller one.

with its evidence table at `:46-48` naming `pairwise_completeness_scan.py:616` (the anchor-relative
predicate) against `run_native_ld_panel.py:878` (`detect_occluded_variants` over **EVERY** deletion in
the window). ⚠ Attribution note: the same fact is also summarised in the STATE ledger's 2026-08-31
entry and in `260831-kw8-SUMMARY.md`, but the **verbatim quote above is from the debug record**, which
is the file v2 cites. This record is added to the v2 checker's `PATHS` as a new key `AR`.

**(ii) The separate pass that answers it** is `src/python/pcs_panelwide_reclassify.py` — the
"PANEL-WIDE RECLASSIFICATION" instrument, which consumes the scan's artifact and classifies which
pairs actually reach the matrix (`12 of 13 pairs and 14 of 15 rows NEVER REACH THE MATRIX. EXACTLY
ONE SURVIVES`).

**(iii) The MEASURED runtimes, each labelled instrument + run + region count:**

| instrument | run | region count | wall time | source at BASIS |
|---|---|---|---|---|
| `pcs_panelwide_reclassify` | **RUN 1**, 2026-09-01 | **6 regions** (1,011,893 rows) | **1 h 53 m** (02:29:11Z → 04:22:50Z, exit 0) | `.planning/quick/260831-kw8-close-seth-s-brief-blind-review-already-/260901-kw8-PANELWIDE-RECLASSIFICATION-as-received.md:13`; region count from `.planning/STATE.md:485` |
| `pcs_panelwide_reclassify` | **RUN 2**, 2026-09-02 | **21 regions carry rows** (manifest `region_ids_selected = 276`) | **2 h 40 m 46 s** (launched 18:26:17Z, outputs 21:07:03Z) | `.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md:10`, `:17-18` |
| pairwise-completeness **scan** (a different instrument) | 2026-09-01 | **21 regions** | **48 min** | `.planning/STATE.md:18` (frontmatter `last_activity`), marker `PRIOR: 2026-09-01 — ✅ SWEEP COMPLETE`, `Runtime 48m not 4h20m` |

**⚠ FINDING — the brief's "1h53m for 21 regions" is FALSE and conflates two runs.** Measured
verbatim at BASIS:

- `260901-kw8-PANELWIDE-RECLASSIFICATION-as-received.md:13` — `Both written Sep 1 04:22Z. Runtime 02:29:11Z -> 04:22:50Z = 1h53m, exit 0, ~99% CPU throughout.`
- `.planning/STATE.md:485` — `runtime is predicted — the 6-region/1h53m/1,011,893-row banked run is given as the`
- `260902-vsp-…/CONTENT-SPEC.md:10` — `both written 2026-09-02T21:07:03Z; launched 18:26:17Z; 2 h 40 m 46 s wall.`
- `260902-vsp-…/CONTENT-SPEC.md:17-18` — `ancestry AFR. region_ids_selected = 276 = the ancestry-resolved MANIFEST size.` / `⚠ 276 is NOT the number of regions carrying rows. 21 regions carry rows. Say this explicitly.`

So **1 h 53 m is the 6-region run**; the 21-region reclassify pass is **2 h 40 m 46 s**. The planner's
correction reproduces exactly. Nothing is reconciled silently.

**(iv) Scalings, recomputed from their stated inputs** (the v2 checker recomputes each):

| scaling | inputs | result |
|---|---|---|
| scan, 21 → 276 regions | 48 min × 276/21 | **630.86 min = 10.51 h** |
| reclassify RUN 2, 21 → 276 regions | 9,646 s × 276/21 | **126,776 s = 35.22 h** |

Both are **linear extrapolations of a measured run over a region count**, not measurements, and v2
labels them as such.

### N6 — mk7ze P88-89 / R255-256: what it actually describes

Verbatim at BASIS:

> *Pre-committed sample.* A systematic-by-span sample of 21 of the 276 AFR regions (20 selected
> by span stratum plus region 1 forced) was fixed BEFORE any result was seen, and measured with

**Measured fact:** this sentence describes the **pre-committed systematic-by-span occlusion SAMPLE**
(21 of 276, 20 by span stratum + region 1 forced). It says nothing about a scan being runnable over
all 276. v1 attaches it to Option D's *scan* sentence (v1:174); v2 attaches it to the **sample**
sentence. (R6 iii.)

### N7 — X1 completeness: what else uploads only under `if ok:`

At BASIS in `src/python/run_native_ld_panel.py` (inside `process_region`):

| item | BASIS lines |
|---|---|
| `if gs_mode:` | `:1244` |
| **`if ok:`** | **`:1245`** |
| verified aggregate `.npz` upload | `:1248-1250` |
| **excludelist** upload (`{region_id}.occluded.excludelist`) | **`:1257-1261`** |
| **occlusion manifest** upload (`{region_id}.occlusion_manifest.tsv`) | **`:1266-1271`** |
| **gate sidecar** upload (`{region_id}.occlusion_gate.json`) | **`:1277-1282`** |
| `else:` / `result["out"] = str(out_npz)  # left in scratch for inspection` | `:1283-1284` |

So a raising region loses **three** egress artifacts, not one: the sidecar (v1's X1), **plus the
excludelist and the occlusion manifest**. (R7 iii.) v1's `c93 :1113-1128` approximation is superseded
by these measured ranges.

### N8 — Option F's ground

| item | BASIS location | verbatim |
|---|---|---|
| verifier OK vocabulary | `fire_verifier.py:300` | `_OK_STATUSES = ("ok", "skipped_idempotent")` |
| verifier deferral vocabulary | `fire_verifier.py:301` | `_DEFERRAL_PREFIXES = ("deferred_infeasible_square", "deferred_occlusion_anomaly")` |
| verifier failure vocabulary | `fire_verifier.py:302-303` | `_FAILURE_STATUSES = ("verify_failed", "error")` / `_FAILURE_PREFIXES = ("error:",)` |
| the `deferred_infeasible_square` **producer site** | `run_native_ld_panel.py:1010` | `result["status"] = (f"deferred_infeasible_square: n_var={pre_window_n_var} "` |
| the R4-COVERAGE registration | `deferred-items.md:1148` | `## R4-COVERAGE — the square-mode deferral set is an ancestry-specific COVERAGE GAP requiring methods/limitations disclosure` |
| its **named enforcer** | `fire_verifier.py:875` | `def check_coverage_disclosure_resolved(path: "str | Path") -> Check:` |

**The structural fact Option F rests on:** `_DEFERRAL_PREFIXES` already contains a `deferred_*` token
(`deferred_infeasible_square`) that is **not** one of the three posted `BRANCH_AFR_OCC_*` branches and
**not** mapped to `BRANCH_AFR_OCC_DEFERRED`. It is an operational verifier-vocabulary status carrying
an in-repo disclosure obligation with a named enforcer. That is a shipped precedent for an operational
`deferred_*` status that makes no claim about the posted branch list.

### N9 — the LOW items' ground at BASIS

| LOW item | citable ground at BASIS? | citation |
|---|---|---|
| (i) a per-region pairwise-completeness **pre-check at fire time**, before the plink/scratch cost it would precede | **YES** | the scratch cost: `run_native_ld_panel.py:866-868` ("~30+ GiB/region … overflows any finite scratch disk"); the ceiling: `READY-TO-FIRE.md:369-370` (`--max-n-var` 120,000); the instrument exists (N5 i/ii) |
| (ii) re-running on a **different sample set** or with **sample-level QC** | **NO** — no posted or in-repo record at BASIS states what a different sample set or sample-level QC would do to this class | v2 states it as an **UNCITED** LOW option, explicitly labelled |
| (iii) the effect on **downstream AFR fine-mapping / coloc denominators** | **NO** — the posted bodies define what happens when the panel stands (trsx5:43) or is reduced (trsx5:45), but there is no record at BASIS of a denominator effect for an **unbanked** region; that absence is itself the §1 sweep finding | v2 states it as an **UNCITED** LOW option, explicitly labelled |

Per the plan: a LOW item with no citable ground is stated as uncited and labelled, never given an
invented citation.

---

## 6. v1's own balance numbers, measured under the DECLARED S-1 contract

Span = `### Option X: …` heading line through the line before the next `###` heading or `## 4.`,
whichever comes first. Tokenization = Python `str.split()` on the raw span, no markdown stripping.

| option | span (v1 lines) | **heading + body** (what `bal:words` scores) | body-only (orientation only) |
|---|---|---|---|
| A | 113–139 | **307** | 296 |
| B | 140–158 | **219** | 208 |
| C | 159–171 | **147** | 136 |
| D | 172–186 | **176** | 165 |
| E | 187–195 | **60** | 49 |
| **max/min** | | **307/60 = 5.12** | 296/49 = **6.04** |

**Reconciliation (A-5).** Both rows were re-measured here, not copied:

- the **body-only** row reproduces the planner's `A 296 / B 208 / C 136 / D 165 / E 49`, ratio
  **6.04**, exactly;
- the **revision brief's** `B = 204` and ratio **5.53** do **NOT** reproduce — measured B body-only is
  **208** and the body-only ratio is **6.04**. ⚠ Reported, not adopted, in either direction;
- the **heading+body** row — which is what `bal:words` actually scores — is
  `A 307 / B 219 / C 147 / D 176 / E 60`, ratio **5.12**, reproducing A-5's declared figures exactly.

Quoting the body-only ratio against a heading+body band would have been an apples-to-oranges
reconciliation; both rows are therefore carried, labelled.

**Why the heading matters (measured):** `(listed for completeness)` sits in Option E's **heading**
(`v1:187`), not its body, so a body-only evaluative screen cannot see it. `bal:eval` scans heading +
body — and, per **A-1**, the **whole draft**, because two of v1's four residual cues sit outside any
option unit at all: `v1:36` (`## 0. Premise corrections: …`) and `v1:68`
(`**So the open question is not halt versus continue.**`).

---

## 7. What this record does NOT do

It authors no v2 text and no checker. It changes no code. It does not touch v1 or
`260916-kht-verify.py` (both re-asserted byte-identical after this commit). It contacts no network,
no cloud, no OSF and no external reviewer. $0.
