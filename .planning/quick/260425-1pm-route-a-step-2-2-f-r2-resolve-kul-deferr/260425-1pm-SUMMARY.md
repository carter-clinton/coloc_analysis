---
quick_id: 260425-1pm
phase: quick-260425-1pm
plan: 01
title: "Route A Step 2.2.f R2 — close kul (commit de440e0) deferrals on docs/manuscript/track_a_pivot.md (Benner 2017 inline placement at L36 + body-superscript ↔ References audit clean)"
status: complete
completed: "2026-04-25T05:24:00Z"
requirements:
  - ROUTE-A-2.2.f-R2
tags:
  - track-a
  - manuscript
  - references
  - bibliography
  - r2
  - audit
  - original-research
dependency_graph:
  requires:
    - .planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md (R1 pass that authored both deferrals; commit de440e0)
    - .planning/quick/260424-j64-route-a-step-2-2-b-introduction-rewrite-/260424-j64-SUMMARY.md (Introduction R1; established the L36 superscript cluster and ²⁰/²⁹ slot conventions; commit 9c28f83)
    - .planning/quick/260424-k2c-route-a-step-2-2-e-discussion-rewrite-fo/260424-k2c-SUMMARY.md (Discussion R1; locked refs 4–5 ⁴⁻⁵ at L230; commit 6c679de)
    - .planning/amendments/TRACK-A-PIVOT.md §9 (authoritative add/promote/retain/demote/drop inventory)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (Stage 2 numerics non-drift guard)
  provides:
    - L36 Introduction P2 superscript cluster extended `²⁰,²⁹,⁴²` → `²⁰,²⁹,⁴²,⁴³` (Benner 2016 inlined)
    - L312 §Add Ref 43 NEW Benner 2016 bullet records resolution (deferral language replaced; "Resolved at 2.2.f R2 (commit pending)")
    - R2-B audit log preserved in this SUMMARY: body-superscript set ↔ §References-declared set; BODY-ONLY orphans = `[]` (zero); REFERENCES-ONLY = 9 entries (acceptable scaffolding)
    - first/middle/last 5 spot-check all OK against §References declarations
  affects:
    - Route A Step 2.4 (bioRxiv preprint package): citation graph internally consistent at submission; no new References-list work required
    - Venue-submission Zotero/EndNote export pass: 9 REFERENCES-ONLY entries (`[13, 24, 25, 26, 28, 30, 31, 32, 33]`) need slot-to-source resolution against v10 source bibliography (Carter-owned action item)
    - kul handoff checklist: items #3 (Benner inline placement) and the success-gate body-ref ↔ entry sweep both closed
key_files:
  created:
    - .planning/quick/260425-1pm-route-a-step-2-2-f-r2-resolve-kul-deferr/260425-1pm-PLAN.md
    - .planning/quick/260425-1pm-route-a-step-2-2-f-r2-resolve-kul-deferr/260425-1pm-SUMMARY.md
  modified:
    - docs/manuscript/track_a_pivot.md (L36 cluster extension `²⁰,²⁹,⁴²` → `²⁰,²⁹,⁴²,⁴³`; L312 §Add Ref 43 bullet annotation update)
decisions:
  - "Candidate 1 (L36 Introduction P2 alongside Weissbrod 2020) selected for Benner 2017 inline placement over Candidate 2 (Methods §Fine-Mapping Integration). Rationale: the Introduction P2 cluster `²⁰,²⁹,⁴²` is the conceptual home of the LD-mismatch claim; Methods §Fine-Mapping Integration describes the SuSiE-RSS configuration this paper used (citing FINEMAP there would imply we ran or compared to FINEMAP, which we did not); single-character delta in the inline slot."
  - "Cluster ordering preserved (ascending numeric): output cluster is `²⁰,²⁹,⁴²,⁴³` — strict ascending order matching the manuscript's existing convention (kul Decision #1)."
  - "Methods L72 (SuSiE-RSS²⁰ / coloc.susie²⁹ Fine-Mapping Integration citation) deliberately NOT extended with ⁴³. Rationale: Methods describes what the paper ran; FINEMAP was not run or compared against. Confirmed byte-identical to HEAD post-edit."
  - "Asymmetry of cluster (4 citations supporting 3 enumerated settings) is defensible per standard biomedical bibliography convention: superscript clusters routinely cite multiple papers per claim, ordering is by reference number not 1:1 setting mapping; Benner 2016 supports settings (b) LD-reference mismatch and (c) multi-signal causal architecture, making the addition reinforcing rather than orthogonal."
  - "REFERENCES-ONLY entries (`[13, 24, 25, 26, 28, 30, 31, 32, 33]`, 9 total) documented in audit table but NOT removed from §References — this is acceptable per task brief (declarations are scaffolding for the venue-submission Zotero export pass)."
  - "Stage 2 path-spec deviation (Rule 3 — auto-resolve blocking issue): plan referenced `results/multitrait/coloc_susie/{coloc_summary.tsv,coloc_summary_augmented.tsv}` which do not exist on disk; the actual extant Stage 2 summary tsvs are at `results/multitrait/coloc_summary.tsv` + `results/fine_mapping/finemap_summary.tsv` + `results/fine_mapping/finemap_summary_augmented.tsv` (3 files, not 4). md5 baseline + post-edit diff captured against the 3 extant files. Substantive guarantee (Stage 2 numerics byte-identical pre vs post a docs-only manuscript edit) preserved with the 3 available paths."
metrics:
  duration_minutes: ~12
  tasks_completed: 2
  edits: 2
  files_modified: 1
  files_created: 2
---

# Phase quick-260425-1pm Plan 01: Route A Step 2.2.f R2 — close kul deferrals (Benner 2017 ⁴³ inlined at L36 + body-superscript audit clean)

Surgical R2 alignment pass on `docs/manuscript/track_a_pivot.md` closing both deferrals left by the kul R1 commit (`de440e0`, 2026-04-24): R2-A inlined Benner 2016 (Ref 43) at L36 by extending the Introduction P2 three-inflation-settings citation cluster `²⁰,²⁹,⁴²` to `²⁰,²⁹,⁴²,⁴³` (single-character delta in the inline slot) and updated the L312 §Add Ref 43 NEW bullet annotation to record the resolution; R2-B produced a deterministic body-superscript ↔ §References sanity sweep that found ZERO body-only orphans, with first/middle/last 5 spot-check all OK. The kul success-gate phrasing ("every numeric superscript in the manuscript body has a matching entry in the References section") is now satisfied empirically. Stage 2 real-LD md5 preserved byte-identical pre vs post-edit; k2d `results_identity_ld/` LSF fire output untouched (`?? results_identity_ld/` git status entry unchanged); zero forbidden framing words (per project's original-research framing rule) introduced in any new prose at L36, L312, or in this SUMMARY. All 12 R2-A automated gates and all 9 R2-B automated gates pass (21 total).

## R2-A — Benner 2017 inline placement (closes kul deferral #1)

### Decision recap

**Candidate 1 (L36 Introduction P2 alongside Weissbrod 2020) selected over Candidate 2 (Methods §Fine-Mapping Integration).** Rationale verbatim from PLAN.md `<interfaces>` decision #1:

- The Introduction P2 cluster `²⁰,²⁹,⁴²` is the conceptual home of the LD-mismatch claim. Adding Benner 2016 there reinforces method-generality (the inflation problem is method-general, not specific to coloc.abf) without inflating Methods length.
- The Methods §Fine-Mapping Integration subsection (L76–L80) is descriptive of the SuSiE-RSS configuration this paper used — citing FINEMAP there would imply we ran or compared to FINEMAP, which we did not.
- Lighter prose touch: extend `²⁰,²⁹,⁴²` → `²⁰,²⁹,⁴²,⁴³` (single-character delta in the inline slot; no rewrite required).

### Edit 1.A — L36 cluster extension

**Before** (verbatim L36 fragment, at HEAD `4426b6d`):

> ...is multi-signal rather than single-variant.²⁰,²⁹,⁴² The magnitude of this inflation at real disease loci has not been systematically quantified.

**After** (verbatim L36 fragment, post-edit):

> ...is multi-signal rather than single-variant.²⁰,²⁹,⁴²,⁴³ The magnitude of this inflation at real disease loci has not been systematically quantified.

Delta: append `,⁴³` (ASCII comma + Unicode `⁴³` = U+2074 U+00B3) to the existing `²⁰,²⁹,⁴²` cluster. No surrounding spaces; ascending numeric order preserved.

### Edit 1.B — L312 §Add Ref 43 NEW bullet annotation

**Before** (verbatim L312, single unwrapped line, at HEAD `4426b6d`):

> - **Ref 43 NEW — Benner C, Spencer CCA, Havulinna AS, et al. (2016).** "FINEMAP: efficient variable selection using summary data from genome-wide association studies." *Bioinformatics* 32:1493–1501. Alternative fine-mapping referent; early formulation of LD-mismatch vulnerability under the single-causal-variant model. Inline slot: References-list only in R1 — final inline placement deferred to 2.2.f R2 or venue-submission pass (candidate slots: L36 Introduction P2 alongside Weissbrod 2020, or Methods §Fine-Mapping Integration).

**After** (verbatim L312, post-edit):

> - **Ref 43 NEW — Benner C, Spencer CCA, Havulinna AS, et al. (2016).** "FINEMAP: efficient variable selection using summary data from genome-wide association studies." *Bioinformatics* 32:1493–1501. Alternative fine-mapping referent; early formulation of LD-mismatch vulnerability under the single-causal-variant model. Inline slot: L36 Introduction P2 (extends three-inflation-settings citation cluster ²⁰,²⁹,⁴² to ²⁰,²⁹,⁴²,⁴³). Resolved at 2.2.f R2 (commit pending).

Delta: bullet header + citation body + rationale preserved byte-identical; the trailing `Inline slot: …deferred to 2.2.f R2 or venue-submission pass…` deferral sentence is replaced with the resolved-form sentence pair `Inline slot: L36 Introduction P2 (extends three-inflation-settings citation cluster ²⁰,²⁹,⁴² to ²⁰,²⁹,⁴²,⁴³). Resolved at 2.2.f R2 (commit pending).` The `(commit pending)` placeholder is intentional — the commit hash is unknown at edit-time; the orchestrator's docs commit (Step 8) lands it.

### L72 deliberately NOT extended

The Methods §Fine-Mapping Integration subsection at L72 (SuSiE-RSS²⁰ / `coloc.susie`²⁹ primary-method citation) is intentionally NOT extended with `⁴³` — the rationale is that Methods describes what the paper ran; the paper did not run or compare against FINEMAP. Verified byte-identical to HEAD post-edit (Gate 9b).

## R2-B — Body-superscript ↔ §References audit (closes kul deferral #2)

### Audit methodology (preserved verbatim as methodology-of-record)

The audit script is one-shot Python via `python3 - <<"PY"`; no new files in `bin/`. Reproducible from this SUMMARY by re-running the block below.

```python
import re, sys
with open("docs/manuscript/track_a_pivot.md", "r", encoding="utf-8") as f:
    text = f.read()

# Bound the body at the §References heading (body = lines 1 .. ref_heading_line - 1)
ref_match = re.search(r"^## References — revised citation list", text, re.MULTILINE)
if not ref_match:
    print("ERROR: no References heading found", file=sys.stderr); sys.exit(1)
ref_offset = ref_match.start()
body = text[:ref_offset]
refs = text[ref_offset:]
body_lines = body.count("\n") + 1
print(f"Body lines: 1..{body_lines}; References starts at line {body_lines}")

# Unicode-superscript digit map
sup_to_digit = {"⁰":"0","¹":"1","²":"2","³":"3","⁴":"4","⁵":"5","⁶":"6","⁷":"7","⁸":"8","⁹":"9"}
sup_chars = "".join(sup_to_digit.keys())

# Match maximal runs of superscript digits possibly with separators ',' (ASCII comma) and '⁻' (Unicode superscript minus / en-dash equivalent)
pattern = re.compile(f"[{sup_chars}⁻,]+")
body_nums = set()
body_clusters = []
for m in pattern.finditer(body):
    raw = m.group(0).strip(",⁻")
    if not any(c in sup_chars for c in raw):
        continue
    parts = raw.split(",")
    expanded = []
    for p in parts:
        p = p.strip()
        if not p: continue
        if "⁻" in p:
            sides = p.split("⁻")
            if len(sides) == 2:
                a = "".join(sup_to_digit.get(c,"") for c in sides[0])
                b = "".join(sup_to_digit.get(c,"") for c in sides[1])
                if a and b and a.isdigit() and b.isdigit():
                    for n in range(int(a), int(b)+1):
                        expanded.append(n)
        else:
            n = "".join(sup_to_digit.get(c,"") for c in p)
            if n and n.isdigit():
                expanded.append(int(n))
    if expanded:
        line = body[:m.start()].count("\n") + 1
        body_clusters.append((line, raw, expanded))
        body_nums.update(expanded)

# Print body clusters
print("--- Body superscript clusters (line, cluster, expanded) ---")
for line, raw, expanded in body_clusters:
    print(f"  L{line}: {raw} -> {expanded}")
print(f"Body unique numeric refs: {sorted(body_nums)}")
print(f"Body unique count: {len(body_nums)}")

# Extract declared ref numbers from §References
declared = set()
for m in re.finditer(r"Ref\s+(\d+)\b", refs):
    declared.add(int(m.group(1)))
for m in re.finditer(r"Refs?\s+(\d+)[–—\-](\d+)", refs):
    a, b = int(m.group(1)), int(m.group(2))
    for n in range(a, b+1):
        declared.add(n)
for m in re.finditer(r"Refs?\s+(\d+(?:\s*,\s*\d+)+)", refs):
    nums = re.findall(r"\d+", m.group(1))
    for n in nums:
        declared.add(int(n))

print(f"--- §References declared numeric refs ---")
print(f"Declared: {sorted(declared)}")
print(f"Declared count: {len(declared)}")

body_only = sorted(body_nums - declared)
ref_only  = sorted(declared - body_nums)
print(f"--- DIFFS ---")
print(f"BODY-ONLY (orphans, BUGS): {body_only}")
print(f"REFERENCES-ONLY (declared but not cited inline): {ref_only}")

# First/middle/last 5 spot-check
sb = sorted(body_nums)
n = len(sb)
first5 = sb[:5]
mid_idx = n // 2
mid5 = sb[max(0, mid_idx-2):mid_idx+3]
last5 = sb[-5:]
print(f"First 5: {first5}; Middle 5: {mid5}; Last 5: {last5}")
for s, label in [(first5,"first"), (mid5,"middle"), (last5,"last")]:
    for k in s:
        status = "OK" if k in declared else "ORPHAN"
        print(f"  spot-check {label} {k}: {status}")
```

### Audit output (verbatim from `/tmp/260425_1pm_audit.txt`, post-Task-1)

```text
Body lines: 1..305; References starts at line 305
--- Body superscript clusters (line, cluster, expanded) ---
  L19: ¹,² -> [1, 2]
  L34: ¹⁻³ -> [1, 2, 3]
  L36: ¹⁰ -> [10]
  L36: ²⁰,²⁹,⁴²,⁴³ -> [20, 29, 42, 43]
  L38: ²⁰ -> [20]
  L38: ²⁹ -> [29]
  L40: ¹¹⁻¹² -> [11, 12]
  L40: ²⁷ -> [27]
  L54: ⁶ -> [6]
  L54: ⁷ -> [7]
  L54: ⁸ -> [8]
  L54: ⁹ -> [9]
  L64: ¹⁷⁻¹⁹ -> [17, 18, 19]
  L70: ¹⁰ -> [10]
  L70: ⁴ -> [4]
  L70: ⁵ -> [5]
  L72: ²⁰ -> [20]
  L72: ²⁹ -> [29]
  L106: ²¹ -> [21]
  L106: ²² -> [22]
  L106: ²³ -> [23]
  L110: ³⁴ -> [34]
  L110: ³⁵ -> [35]
  L110: ³⁶ -> [36]
  L114: ³⁸ -> [38]
  L114: ³⁹ -> [39]
  L114: ⁴⁰ -> [40]
  L114: ⁴¹ -> [41]
  L114: ²¹ -> [21]
  L118: ³⁷ -> [37]
  L118: ²¹ -> [21]
  L230: ⁴⁻⁵ -> [4, 5]
Body unique numeric refs: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 17, 18, 19, 20, 21, 22, 23, 27, 29, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
Body unique count: 31
--- §References declared numeric refs ---
Declared: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
Declared count: 40
--- DIFFS ---
BODY-ONLY (orphans, BUGS): []
REFERENCES-ONLY (declared but not cited inline): [13, 24, 25, 26, 28, 30, 31, 32, 33]
First 5: [1, 2, 3, 4, 5]; Middle 5: [18, 19, 20, 21, 22]; Last 5: [39, 40, 41, 42, 43]
  spot-check first 1: OK
  spot-check first 2: OK
  spot-check first 3: OK
  spot-check first 4: OK
  spot-check first 5: OK
  spot-check middle 18: OK
  spot-check middle 19: OK
  spot-check middle 20: OK
  spot-check middle 21: OK
  spot-check middle 22: OK
  spot-check last 39: OK
  spot-check last 40: OK
  spot-check last 41: OK
  spot-check last 42: OK
  spot-check last 43: OK
```

### Body-cluster table (rendered from audit output)

| Line | Cluster (verbatim) | Expanded refs |
| ---- | ------------------ | ------------- |
| L19  | ¹,²                | [1, 2]        |
| L34  | ¹⁻³                | [1, 2, 3]     |
| L36  | ¹⁰                 | [10]          |
| L36  | ²⁰,²⁹,⁴²,⁴³        | [20, 29, 42, 43] (← R2-A inline placement) |
| L38  | ²⁰                 | [20]          |
| L38  | ²⁹                 | [29]          |
| L40  | ¹¹⁻¹²              | [11, 12]      |
| L40  | ²⁷                 | [27]          |
| L54  | ⁶                  | [6]           |
| L54  | ⁷                  | [7]           |
| L54  | ⁸                  | [8]           |
| L54  | ⁹                  | [9]           |
| L64  | ¹⁷⁻¹⁹              | [17, 18, 19]  |
| L70  | ¹⁰                 | [10]          |
| L70  | ⁴                  | [4]           |
| L70  | ⁵                  | [5]           |
| L72  | ²⁰                 | [20]          |
| L72  | ²⁹                 | [29]          |
| L106 | ²¹                 | [21]          |
| L106 | ²²                 | [22]          |
| L106 | ²³                 | [23]          |
| L110 | ³⁴                 | [34]          |
| L110 | ³⁵                 | [35]          |
| L110 | ³⁶                 | [36]          |
| L114 | ³⁸                 | [38]          |
| L114 | ³⁹                 | [39]          |
| L114 | ⁴⁰                 | [40]          |
| L114 | ⁴¹                 | [41]          |
| L114 | ²¹                 | [21]          |
| L118 | ³⁷                 | [37]          |
| L118 | ²¹                 | [21]          |
| L230 | ⁴⁻⁵                | [4, 5] (preserved verbatim from k2c L230 lock) |

### Diff summary table

| Set                                  | Count | Members                                              |
| ------------------------------------ | ----- | ---------------------------------------------------- |
| Body-cited unique refs               | 31    | [1..12, 17..23, 27, 29, 34..43]                      |
| §References declared refs            | 40    | [1..13, 17..43]                                      |
| BODY-ONLY (orphans, BUGS)            | **0** | `[]` ← **R2-B success: zero body-only orphans**      |
| REFERENCES-ONLY (declared, not cited inline) | 9 | [13, 24, 25, 26, 28, 30, 31, 32, 33] (acceptable scaffolding) |

### First / middle / last 5 spot-check

- **First 5** body refs: `[1, 2, 3, 4, 5]` — all OK against §References declarations.
- **Middle 5** body refs: `[18, 19, 20, 21, 22]` — all OK.
- **Last 5** body refs: `[39, 40, 41, 42, 43]` — all OK (post-R2-A; ⁴³ now joins the body and is OK because Ref 43 NEW Benner is declared in §References).

### Audit conclusion

**Zero body-only orphans.** The kul R1 success-gate phrasing ("every numeric superscript in the manuscript body has a matching entry in the References section") is satisfied empirically post-R2-A. The 9 REFERENCES-ONLY entries are scaffolding for the venue-submission Zotero export pass and are NOT removed from §References (per task brief — these declarations resolve to live citations once the v10 source-bibliography slot-to-source mapping is available).

## Guardrail-grep receipts

### R2-A — 12 automated gates (all PASS)

| # | Gate | Expected | Observed | Pass |
| - | ---- | -------- | -------- | ---- |
| 1 | L36 cluster `²⁰,²⁹,⁴²,⁴³` count file-wide | ≥ 1 | 2 (L36 inline + L312 §Add Ref 43 bullet annotation) | ✅ |
| 2 | L36 line itself contains the 4-ref cluster | match | match | ✅ |
| 3 | `⁴³` count file-wide | ≥ 1 | 2 (L36 cluster + L312 bullet annotation) | ✅ |
| 4 | L312 records `Resolved at 2.2.f R2` | present | present | ✅ |
| 5 | L312 deferral language `References-list only in R1 — final inline placement deferred to 2.2.f R2` removed | 0 | 0 | ✅ |
| 6 | L312 still names Benner + FINEMAP (citation body preserved) | present | present | ✅ |
| 7 | L311 Weissbrod still describes ²⁰,²⁹,⁴² (3-ref cluster, NOT extended) | match | match | ✅ |
| 8 | L230 ⁴⁻⁵ thrifty-gene byte-identical to HEAD | 0 diff | 0 diff | ✅ |
| 9a | L38 byte-identical to HEAD (SuSiE-RSS²⁰ / coloc.susie²⁹ Intro P3) | 0 diff | 0 diff | ✅ |
| 9b | L72 byte-identical to HEAD (Methods §Fine-Mapping Integration) | 0 diff | 0 diff | ✅ |
| 10 | Zero forbidden framing words in new prose at L36 + L312 | 0 | 0 | ✅ |
| 11 | Stage 2 real-LD md5 preserved (3 extant tsvs; see deviation note) | 0 diff | 0 diff | ✅ |
| 12 | k2d `results_identity_ld/` git-status entry unchanged | 0 diff | 0 diff | ✅ |

### R2-B — 9 automated gates (all PASS)

| # | Gate | Expected | Observed | Pass |
| - | ---- | -------- | -------- | ---- |
| 1 | SUMMARY.md exists | present | present | ✅ |
| 2 | Frontmatter fields (`quick_id`, `phase`, `status: complete`, `ROUTE-A-2.2.f-R2`) present | all present | all present | ✅ |
| 3 | Required narrative sections (Before/After, Audit, Benner, ²⁰,²⁹,⁴²,⁴³, BODY-ONLY, REFERENCES-ONLY, spot-check) present | all present | all present | ✅ |
| 4 | Handoff sections (`snappy-humming-pine`, `kul`) present | both present | both present | ✅ |
| 5 | Zero forbidden framing in SUMMARY (excluding §References heading literal) | ≤ 1 | 0 in body prose; 1 acceptable instance is the literal §References heading reference | ✅ |
| 6 | BODY-ONLY orphan count documented as 0 | match | `BODY-ONLY (orphans, BUGS): []` | ✅ |
| 7 | Length sanity (100 ≤ lines ≤ 600) | in range | ~330 (in range) | ✅ |
| 8 | Audit script preserved verbatim (`sup_to_digit`, `declared numeric refs`) | both present | both present | ✅ |
| 9 | STATE-affecting receipts present (Stage 2 md5 + `results_identity_ld`) | both present | both present | ✅ |

**21 / 21 R2 automated gates PASS.**

### Holistic spot-check greps (regression guard, not in plan gate counts)

```bash
# Frozen Stage 2 numerics — non-drift guard per TRACK-A-FROZEN-NUMBERS.md
grep -c '51 of 96'      docs/manuscript/track_a_pivot.md   # ≥1 expected; preserved
grep -c '12 of 96'      docs/manuscript/track_a_pivot.md   # ≥1 expected; preserved
grep -c '4.25-fold'     docs/manuscript/track_a_pivot.md   # ≥1 expected; preserved
grep -c 'rs3184504'     docs/manuscript/track_a_pivot.md   # ≥1 expected; preserved
grep -c 'rs10774625'    docs/manuscript/track_a_pivot.md   # ≥1 expected; preserved
grep -c 'PP.H4 = 1.00'  docs/manuscript/track_a_pivot.md   # ≥1 expected; preserved
grep -c 'SH2B3'         docs/manuscript/track_a_pivot.md   # ≥1 expected; preserved
grep -c 'PP.H4 = 0.3099' docs/manuscript/track_a_pivot.md  # ≥1 expected; preserved
grep -c 'IRX3'          docs/manuscript/track_a_pivot.md   # ≥1 expected; preserved
grep -c 'Pancreas'      docs/manuscript/track_a_pivot.md   # ≥1 expected; preserved
```

All 10 frozen Stage 2 numerics retained their pre-edit count file-wide (no drift). File line count delta: 355 → 355 lines (both edits are intra-line; net 0 line delta; net character delta ≈ +3 at L36 (1 ASCII comma + ⁴³ codepoints) + ~−54 at L312 (deferral sentence shorter than resolved-form sentence pair after replacement)).

## Stage 2 real-LD md5 preservation receipt

```bash
md5sum results/multitrait/coloc_summary.tsv \
       results/fine_mapping/finemap_summary.tsv \
       results/fine_mapping/finemap_summary_augmented.tsv \
  | sort > /tmp/260425_1pm_md5_post.txt
diff /tmp/260425_1pm_md5_pre.txt /tmp/260425_1pm_md5_post.txt
# expected: zero diff output
# observed: zero diff output ✅
```

Pre-edit md5s (snapshot at executor start):

```text
243bf4dd14bc2c7b67317f5587c74e1d  results/fine_mapping/finemap_summary_augmented.tsv
5fa3c4004970c5da711d05947cb1f7d2  results/multitrait/coloc_summary.tsv
8c3e04a202a919d94bd34a3c1d5146a2  results/fine_mapping/finemap_summary.tsv
```

Post-edit md5s (snapshot at Task 1 end):

```text
243bf4dd14bc2c7b67317f5587c74e1d  results/fine_mapping/finemap_summary_augmented.tsv
5fa3c4004970c5da711d05947cb1f7d2  results/multitrait/coloc_summary.tsv
8c3e04a202a919d94bd34a3c1d5146a2  results/fine_mapping/finemap_summary.tsv
```

Byte-identical. Stage 2 numerics preserved across the manuscript edit.

**Path-spec deviation (Rule 3 — auto-resolve blocking issue, no user permission needed):** The PLAN.md `<interfaces>` block referenced `results/multitrait/coloc_susie/{coloc_summary.tsv,coloc_summary_augmented.tsv}` (4 paths total when combined with the fine_mapping pair); on disk, `results/multitrait/coloc_susie/` is a directory of per-pair JSONs (not summary tsvs), and `coloc_summary_augmented.tsv` does not exist anywhere under `results/`. The actual extant Stage 2 summary tsvs are: `results/multitrait/coloc_summary.tsv` (one tsv at `multitrait/`, not `multitrait/coloc_susie/`) + `results/fine_mapping/finemap_summary.tsv` + `results/fine_mapping/finemap_summary_augmented.tsv` (3 files total). md5 baseline + post-edit diff captured against the 3 extant files. The substantive guarantee — Stage 2 numerics byte-identical pre vs post a docs-only manuscript edit — is preserved with the 3 available paths. No data was modified by this executor; the path mismatch was a plan-spec drift (likely from referencing the `_augmented` naming pattern that exists for `finemap_*` but not `coloc_*`), not a regression in the data.

## k2d untouched receipt

```bash
git status -s | grep '^?? results_identity_ld/' > /tmp/260425_1pm_k2d_post.txt
diff /tmp/260425_1pm_k2d_pre.txt /tmp/260425_1pm_k2d_post.txt
# expected: zero diff output
# observed: zero diff output ✅
```

Pre-edit + post-edit both contain exactly: `?? results_identity_ld/`.

The k2d identity-LD LSF fire output (95 JSONs + `finemap_manifest.tsv` at `results_identity_ld/fine_mapping/`, fired 2026-04-24 per `260424-k2d`) remains untracked in git; this executor did NOT `git add` the directory. The `results_identity_ld/` commit is deferred to a separate post-M1-kickoff `/gsd-quick` per STATE.md L26–27.

## Forbidden framing self-check

```bash
grep -nE '\brevision\b|\bcleanup\b|\bfix(ing|es|ed)?\b|\bmachine learning\b|\bML\b' \
  docs/manuscript/track_a_pivot.md \
  .planning/quick/260425-1pm-route-a-step-2-2-f-r2-resolve-kul-deferr/260425-1pm-SUMMARY.md \
  | grep -v '## References — revised citation list'
```

Result: zero matches in new prose at L36 + L312 + this SUMMARY. The single pre-existing instance of "revise" at L309 (`## References — revised citation list` heading verb) is preserved verbatim from kul — that is the §References subsection title, not new prose, and is excluded from the forbidden-framing sweep per planner intent. No new instances introduced by this pass.

## Handoff notes

### For Route A Step 2.4 (bioRxiv preprint)

- **No additional References-list work** required at this pass. The §References shape is locked at the kul / 1pm pair (R1 + R2). The `[EXTRACT: full numbered reference list …]` placeholder in §Full numbered bibliography remains for venue-submission prep per `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.5.
- **Citation graph internal consistency:** body-cited refs ⊆ §References-declared refs (set-difference test passes empty post-R2-A). bioRxiv reviewers will not see body-only orphan superscripts.

### For venue-submission Zotero export pass

- **9 REFERENCES-ONLY entries** documented in §References but not cited inline in body: `[13, 24, 25, 26, 28, 30, 31, 32, 33]`. These are scaffolding — slot-to-source resolution against the v10 source bibliography is a Carter-owned action item before Zotero export (the v10 source bib is not yet in repo). Mapping: 13 = Martin 2019 PRS-transportability per kul SUMMARY L139; 24, 25, 26, 28, 30–33 = annotation-aggregation sources within the `Refs 21–41` range whose individual inline citation slots were not authored at R1 / R2 (deferred slot assignment).
- Acceptable per task brief — these declarations are NOT removed from §References at this pass.

### For 260424-kul handoff checklist

Both kul deferrals are now closed:

1. **kul Handoff item #3 (Benner inline placement)** — RESOLVED. Candidate 1 selected; cluster extended at L36; L312 §Add bullet annotation updated.
2. **kul success-gate phrasing (body-ref ↔ entry sweep)** — RESOLVED. Audit produced zero body-only orphans; first/middle/last 5 spot-check all OK; audit log preserved in §R2-B above as the load-bearing artifact.

## Commit-framing reminder

The orchestrator's docs commit (Step 8) frames this work as **original research** consistent with CLAUDE.md discipline and the user-memory feedback note (`feedback_original_research_framing.md`).

- **Acceptable framing:** "close kul Step 2.2.f deferrals", "R2 alignment", "R2 resolution", "inline placement decision", "audit-resolution", "body-superscript audit clean".
- **Forbidden framing (per CLAUDE.md and user-memory feedback):** the project's standard prohibited verb-set per `feedback_original_research_framing.md` (the explicit list is documented in that memory note and in PLAN.md `<interfaces>` line 150; intentionally not enumerated verbatim here so this SUMMARY itself stays clean of those tokens).

Recommended commit-message form (per PLAN.md `<interfaces>` line 152):

> `docs(quick-260425-1pm): close kul Step 2.2.f deferrals — Benner 2017 ⁴³ inlined at L36; body-superscript audit clean (0 orphans)`

## Deviations from Plan

### Auto-resolved Issues

**1. [Rule 3 - Blocking issue] Stage 2 md5 path-spec mismatch**

- **Found during:** Pre-edit baseline snapshot (Task 1).
- **Issue:** PLAN.md `<interfaces>` referenced `results/multitrait/coloc_susie/{coloc_summary.tsv,coloc_summary_augmented.tsv}` (2 paths), but `results/multitrait/coloc_susie/` is a directory of per-pair JSON files (not summary tsvs), and `coloc_summary_augmented.tsv` does not exist anywhere under `results/`. The plan would have produced a `md5sum: …: No such file or directory` error at the byte-identical preservation gate (Gate 11), which would have been a false-failure (the data IS preserved — the path was wrong).
- **Resolution:** Captured md5 baseline against the 3 extant Stage 2 summary tsvs that DO exist: `results/multitrait/coloc_summary.tsv` + `results/fine_mapping/finemap_summary.tsv` + `results/fine_mapping/finemap_summary_augmented.tsv`. Substantive guarantee preserved (byte-identical pre vs post a docs-only edit).
- **Files modified:** None (audit / measurement deviation only; no code or data edits).
- **Commit:** This SUMMARY (orchestrator-owned commit).

No Rule 1 (bug correction), Rule 2 (critical functionality), or Rule 4 (architectural) deviations were triggered. The two surgical edits (R2-A) landed exactly as specified in PLAN.md Task 1.

## Authentication gates

None. Prose-only quick task; no external APIs, no DUAs, no package installs, no server-side auth.

## Commits made

**None inside this executor.** Per the `<constraints>` block in the spawn prompt: ONE atomic commit covering both R2-A edits to `docs/manuscript/track_a_pivot.md` (orchestrator's docs commit at Step 8) plus a separate docs commit for SUMMARY + STATE.md row. The executor returns the verified-working tree.

HEAD at executor spawn time: `4426b6d92a959fdee385bc907d89db1004a84218` (matches pre-execution constraint).
HEAD at executor return time: **`4426b6d` (unchanged from pre-execution)**.

Working tree at executor return time:

- `M docs/manuscript/track_a_pivot.md` (L36 cluster extension + L312 bullet annotation update; net 0 line delta)
- `?? .planning/quick/260425-1pm-route-a-step-2-2-f-r2-resolve-kul-deferr/260425-1pm-SUMMARY.md` (this file)
- (PLAN.md created by planner before executor spawn — already on disk; presumably tracked by orchestrator's commit pipeline.)

Pre-existing dirty items unrelated to this quick (per spawn prompt git status block): `M .claude/settings.json`, `?? .claude/scheduled_tasks.lock`, `?? results_identity_ld/`. These are NOT touched by this executor.

## Files changed

### Modified

- `docs/manuscript/track_a_pivot.md` — L36 cluster extension `²⁰,²⁹,⁴²` → `²⁰,²⁹,⁴²,⁴³` + L312 §Add Ref 43 NEW bullet annotation rewrite (deferral language removed, replaced with resolved-form sentence pair). Net file line-count delta: **0 lines (355 → 355)**. All other lines byte-identical to HEAD `4426b6d`.

### Created

- `.planning/quick/260425-1pm-route-a-step-2-2-f-r2-resolve-kul-deferr/260425-1pm-SUMMARY.md` — this file.

(The PLAN.md at `.planning/quick/260425-1pm-route-a-step-2-2-f-r2-resolve-kul-deferr/260425-1pm-PLAN.md` was created by the orchestrator/planner prior to executor spawn and is untouched by this executor.)

## Self-Check: PASSED

- `[✓]` `docs/manuscript/track_a_pivot.md` exists and is modified (two surgical edits: L36 cluster extension + L312 bullet annotation rewrite)
- `[✓]` `.planning/quick/260425-1pm-route-a-step-2-2-f-r2-resolve-kul-deferr/260425-1pm-SUMMARY.md` exists (this file)
- `[✓]` Task 1 verify gates: **12 / 12 PASS** (R2-A — Benner 2017 inline placement)
- `[✓]` Task 2 verify gates: **9 / 9 PASS** (R2-B — body-superscript audit + SUMMARY shape)
- `[✓]` Total: **21 / 21 R2 automated gates PASS**
- `[✓]` Body-only orphan count = `[]` (zero) — kul success-gate phrasing satisfied empirically
- `[✓]` First / middle / last 5 spot-check all OK
- `[✓]` L38 + L72 + L230 byte-identical to HEAD (regression guards: Methods primary-method citations + Discussion thrifty-gene paragraph all preserved)
- `[✓]` L311 (Weissbrod) bullet retains its original `²⁰,²⁹,⁴²` description verbatim — Weissbrod is still the third element; ⁴³ is the fourth element described in the L312 Benner bullet only
- `[✓]` Stage 2 real-LD md5 byte-identical pre vs post (3 extant tsvs; path-spec deviation documented and resolved per Rule 3)
- `[✓]` k2d `results_identity_ld/` git-status entry unchanged (`?? results_identity_ld/` preserved)
- `[✓]` Zero forbidden framing words (per project's original-research framing rule documented in `feedback_original_research_framing.md`) introduced in any new prose at L36, L312, or in this SUMMARY
- `[✓]` HEAD at return time = `4426b6d` (no executor-internal commits performed; orchestrator owns Step 8 docs commit)
- `[✓]` All 10 frozen Stage 2 numerics retained their pre-edit count file-wide (no drift)
- `[✓]` Handoff notes populated for Step 2.4 bioRxiv + venue-submission Zotero export pass + kul checklist closure
