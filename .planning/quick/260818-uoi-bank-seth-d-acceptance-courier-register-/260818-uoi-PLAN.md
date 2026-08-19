---
phase: quick-260818-uoi
plan: 01
type: execute
wave: 1
depends_on: []
mode: quick-full
autonomous: true
requirements: [UOI-01, UOI-02, UOI-03, UOI-04]
files_modified:
  - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
  - .planning/HANDOFF.json          # OPTIONAL — Task 2 step 5; skip unless every guard is clean
  - .planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SUMMARY.md

must_haves:
  truths:
    - "Seth's 2026-08-18 D-01..D-13 acceptance courier is banked in-repo and cited by every artifact that acts on it."
    - "A reader of deferred-items.md can find, under one item id, the decision NOT to build the cross-cohort MAF join and the within-panel missingness test that replaces it."
    - "That item states which of its own premises were MEASURED against the shipped code and which are Seth's unverified claims, distinguishably."
    - "Seth's two cross-cohort join constraints ((CHR,POS)-only key; MAF = min(EAF,1-EAF)) survive VERBATIM, so a future implementer cannot reconstruct them from a paraphrase."
    - "D-11 (region-1 severity stays FINDING, no change requested) is recorded as a concurrence and NO code changed anywhere."
    - "A browser agent reading the Stage-B block of either runbook that carries the MAF note is told the cross-cohort join is NOT to be built and is given the registered item id to point Carter at."
    - "The R4-COVERAGE block that the live fire_verifier gate parses is byte-unchanged (modulo trailing whitespace) after the append."
    - "260817-vbu-verify.sh produces byte-identical output before and after every runbook edit."
    - "Every file touched shows ZERO deleted lines in git diff --numstat."
  artifacts:
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md"
      provides: "The MISS-1 registered deferral (within-panel missingness test) appended after R4-COVERAGE"
      contains: "## MISS-1"
      min_lines: 1240
    - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md"
      provides: "Stage-B (STEP 9-GATE) A-12 note retargeted from 'Carter's planning-side work' to 'NOT to be built; see MISS-1'"
      contains: "MISS-1"
    - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md"
      provides: "Same retarget in the browser-agent paste copy (§9b Stage-B gate block)"
      contains: "MISS-1"
    - path: ".planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SUMMARY.md"
      provides: "Close-out: the 13 acceptances banked, D-11 concurrence, the redirect, the measured premises, the guard transcript"
      contains: "MISS-1"
  key_links:
    - from: ".planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md (MISS-1)"
      to: ".planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SETH-COURIER-d-acceptance-as-received.md"
      via: "explicit relative path citation in the item body"
      pattern: "260818-uoi-SETH-COURIER-d-acceptance-as-received"
    - from: "260812-ox1-AGENT-PROMPT.md STEP 9-GATE note"
      to: "deferred-items.md MISS-1"
      via: "item id named in the retargeted note"
      pattern: "MISS-1"
    - from: "260812-ox1-BROWSER-PASTE.md §9b Stage-B block"
      to: "deferred-items.md MISS-1"
      via: "item id named in the retargeted note"
      pattern: "MISS-1"
---

<objective>
Bank the outcome of Seth's 2026-08-18 acceptance courier as RECORDS ONLY.

Two actionable outcomes, zero code:

1. **D-11 CONCURRENCE.** Seth asked for no change: region-1 severity stays
   `FINDING`. This is recorded in prose (the MISS-1 item + the SUMMARY) and
   nowhere else. **No edit to `src/python/fire_verifier.py`, `tests/m3/`,
   `config/`, or any Snakefile. None. If you find yourself opening a `.py`
   file to write, you have misread this plan.**

2. **MAF-DEPRESSION REDIRECT.** The cross-cohort `(panel_maf, sumstats_maf)`
   join is NOT to be built. Register the within-panel missingness test in its
   place as a POST-FIRE deferred item (`MISS-1`), and retarget the Stage-B
   "do not improvise this" note in the runbooks so a browser agent — and
   Carter — is pointed at the registered item instead of at a join nobody
   intends to build.

Purpose: quick-260818-sml left the runbooks saying the MAF join is "Carter's
planning-side work, not yours." As of Seth's courier that sentence is FALSE —
it is nobody's work. A runbook that describes retired work as pending is how a
fire-time agent improvises. This task makes the record match the decision.

Output: one appended `## MISS-1` section in `deferred-items.md`; two retargeted
runbook notes; an optional one-clause `HANDOFF.json` gate append; a SUMMARY.

⛔ **AN AGENT MUST NEVER FIRE.** No perimeter contact, no `gsutil`/`gcloud`/`bq`/
`wb`, no network, no OSF. Push is the orchestrator's, not yours.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SETH-COURIER-d-acceptance-as-received.md

<!-- Read ONLY the R4-COVERAGE section (line 1146 to EOF) and the file's first 10
     lines for the item format. Do not read the whole 1,197-line file; you are
     appending, not editing. -->
@.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md

<interfaces>
<!-- MEASURED at plan time, 2026-08-18, against HEAD. These are the contracts your
     edits must not break. Do NOT re-derive them by exploration — they are here so
     you don't have to. DO re-measure the BEFORE values at execution time (a
     hardcoded hash pin is a timebomb; a before/after comparison is not). -->

### Enforcer 1 — `src/python/fire_verifier.py` parses `deferred-items.md` BY HEADING

```python
_R4_HEADING      = re.compile(r"^## R4-COVERAGE(?![-\w])", re.M)
_SECTION_HEADING = re.compile(r"^## ", re.M)

def _extract_r4_block(text: str) -> str:
    m = _R4_HEADING.search(text)
    if m is None:
        return ""
    start = m.start()
    nxt = _SECTION_HEADING.search(text, m.end())
    return text[start:nxt.start()] if nxt else text[start:]
```

**The consequence that drives Task 1's append shape.** Today the R4 block runs
from `## R4-COVERAGE` to **EOF** (measured: terminator == EOF; 2,776 B; 41
non-empty lines; md5 `414221df56317fdd6a23cb876452940f`). `_SECTION_HEADING`
matches `^## ` and **NOT** `^# `. So:

| Append shape                                | Effect on the parsed R4 block |
|---------------------------------------------|-------------------------------|
| starts with `## MISS-1 — …`                  | block terminates at the new heading → content **byte-identical modulo one trailing newline**. ✅ |
| starts with `# Deferred items — discovered…` | the `# ` banner is **absorbed INTO the R4 block** → the gate's input silently grows. ❌ |

The file's older sections each open with a `# Deferred items — discovered during
… execution (date)` banner. **Do not follow that convention here.** It was safe
before `fire_verifier.py` existed; it is not safe now. Fold the provenance into
the `## ` heading line and a `**Logged:**` line inside the item body — which is
exactly what the R4-COVERAGE item itself already does.

Downstream of the extractor (informational — all of these stay RED-by-design
today and Task 1 must not change that):
`_R4_ESTIMATE_SENTINELS = ("29 / 276 = 10.5%", "Seth's estimates, not measurements", "~247 regions", "48.5 Mb", "~10.5%")`;
`_R4_MIN_BLOCK_LINES = 8`; a `^\s*MEASURED:` provenance line is required once the
sentinels are gone. The live gate is
`tests/m3/test_fire_verifier.py::…` which **skips** until a measured panel TSV
lands in-repo — that skip IS the enforcer.

### Enforcer 2 — `260817-vbu-verify.sh` pins the trsx5 card ranges (must stay green)

```
card_checks AGENT-PROMPT  "$(block "$AP" '^STEP 6b' '^STEP 7')"
card_checks BROWSER-PASTE "$(block "$BP" '^## 6b'   '^## 7')"
card_checks READY-TO-FIRE "$(block "$RF" '^## 6b'   '^## 7[.]')"
```

MEASURED pinned ranges at HEAD — **every Task 2 edit must land OUTSIDE these**:

| File | pinned lines | your edit target |
|---|---|---|
| `260812-ox1-AGENT-PROMPT.md` | **106–163** (`STEP 6b` → `STEP 7`) | lines **271–277** ✅ outside |
| `260812-ox1-BROWSER-PASTE.md` | **107–179** (`## 6b` → `## 7`) | lines **371–377** ✅ outside |
| `260812-ox1-READY-TO-FIRE.md` | 116–200 | **no MAF note exists — do not add one** |

Baseline MEASURED at plan time: `bash 260817-vbu-verify.sh all` → **20 PASS, 0
FAIL, exit 0**.

### Enforcer 3 — `260814-guk-verify.sh record` (R8 reads `deferred-items.md`)

```bash
nret="$(grep -ci 'nothing scientific is lost' "$DI" || true)"
nretired="$(grep -i 'nothing scientific is lost' "$DI" | grep -c 'RETIRED' || true)"
# FAIL unless nret > 0 AND nret == nretired
# section_fire F10: 'nothing scientific is lost' AND 'nothing is lost' must each
#                   appear 0 times across AP+BP+RF (measured today: 0 and 0)
```

⚠ **`260814-guk-verify.sh record` is ALREADY RED at HEAD and that is NOT yours.**
MEASURED baseline: `R1 PASS, R2 PASS, R3 FAIL, R4 FAIL, R5 PASS, R6 PASS, R7
PASS, R8 PASS`. R3/R4 are pre-existing drift over `HANDOFF.json`'s `status` and
`resume_on_reconnect[0]`. **The pass criterion is therefore an EMPTY OUTPUT DIFF,
never "exit 0".** Do not "fix" R3/R4; they are out of scope.

Forbidden strings anywhere you write (they would flip R8/F10):
`nothing scientific is lost`, `nothing is lost`.
Also: **no appended line may begin with `## R4-COVERAGE`** (it would steal the
`_R4_HEADING` first-match).

### Enforcer 4 — `HANDOFF.json` byte round-trip (only if you do Task 2 step 5)

MEASURED: 75,604 B; 40 top-level keys; and
`json.dumps(d, indent=2, ensure_ascii=False)` reproduces the file **byte-identically
with NO trailing newline** (verified `True` at plan time). guk `record` pins
`gates.trsx5_posted_body` (R2 PASS), `status` (R3, already FAIL) and
`resume_on_reconnect[0]` md5 (R4, already FAIL) — **do not touch any of those
three keys.**

### MEASURED premises for the MISS-1 item body (verify, don't trust this table)

| Premise | How it was measured at plan time | Verdict |
|---|---|---|
| `.lmiss` is not emitted by the fire | `grep -rn 'lmiss\|--missing' src/` → **0 hits**; `aou_ld_panel.build_plink_ld_command` docstring enumerates the square-mode argv as `--r square bin4` + `--keep-allele-order` + `--mac 1 --nonfounders --write-snplist` over `--chr/--from-bp/--to-bp` — no `--missing` | **TRUE** |
| `check_maf_depression` is implemented but unwired | `src/python/fire_verifier.py:632` (impl, with an `⚠ A-12: IMPLEMENTED BUT NOT WIRED` docstring at :640); tests at `tests/m3/test_fire_verifier.py:641+` | **TRUE** |
| the bfile + VM persist post-fire | `HANDOFF.json.cluster`: the n1-standard-32 holding `/home/jupyter/afr_cohort` is "STOPPED, not deleted — preserved for the fire". Runbooks say **STOP** the env (`AGENT-PROMPT:279`, `BROWSER-PASTE:301`); STEP C/D/E/F/G contains **no VM teardown step** | **CONSISTENT, but NOT GUARANTEED** — no runbook step commits to keeping it after STEP G, and AoU envs on a STANDARD disk lose everything on delete. The item must say so. |
| region-1 2×2, `fAmB = 1.0` in 5 of 6 pairs | `grep -rln 'fAmB'` → appears **only** in Seth's banked courier | **SETH'S CLAIM, NOT INDEPENDENTLY RECORDED IN-REPO** — attribute it, never assert it as ours. |
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Register MISS-1 in deferred-items.md, append-only, with the R4 block proven unmoved</name>

  <files>
.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
  </files>

  <action>
**Step 0 — capture the BEFORE, mechanically. Do this before you type one character
of prose.** Write to the scratchpad (never into the repo):

```bash
S="$SCRATCH"   # the session scratchpad dir given to you; NOT /tmp, NOT the repo
bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh record > "$S/guk-record.before.txt" 2>&1
bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all  > "$S/vbu-all.before.txt"    2>&1
```

**Step 1 — append ONE section at EOF.** The first appended line MUST be the `## `
heading (see the interfaces table: a `# ` banner would be swallowed by the R4
extractor). Do not touch any existing byte. Suggested opening:

```
## MISS-1 — the MAF-depression follow-up is REDIRECTED to a WITHIN-PANEL missingness test (registered during quick-260818-uoi, 2026-08-18)
```

The body MUST contain all nine elements below. Wording is yours; the *content*
is not negotiable.

1. **`**Logged:** 2026-08-18 (`quick-260818-uoi`, from Seth's 2026-08-18
   D-01…D-13 acceptance courier).`** plus the relative path to the banked
   courier: `.planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SETH-COURIER-d-acceptance-as-received.md`.
   **Status line: REGISTERED as a POST-FIRE follow-up — not blocking the fire, no
   producer change now.**

2. **The redirect, stated as a decision.** The cross-cohort
   `(panel_maf, sumstats_maf)` join is **NOT to be built.** Seth's reason,
   preserved as reasoning not just conclusion: the GWAS AFR cohort is not the AoU
   AFR cohort, region 1's ratio is 0.0078 / 0.014 = 0.557 — the direction the
   mechanism predicts, but ordinary between-cohort AF differences at MAF ≈ 0.01
   are easily that large on their own, so a red would be ambiguous and **an
   ambiguous gate is one people learn to ignore.**

3. **The replacement test, specified precisely enough to implement.** The
   mechanism's direct prediction is **callability, not MAF**: a variant covered by
   a deletion's REF span is uncallable on the deletion haplotype, so its
   per-variant missingness should be elevated relative to the region-wide `F_MISS`
   distribution. Per region, compare `F_MISS` of the occlusion-excluded variants
   against the region's own `F_MISS` distribution — a rank-based test, or simply
   the fraction of excluded variants above the region's 90th percentile.
   **Elevated ⇒ mechanism-consistent. Not elevated ⇒ a genuine FINDING, and a
   cleaner one, because there is no second cohort to blame.**
   Record why it is better evidence: **single-cohort** (no cross-cohort confound)
   and **egress-safe** (aggregate per-variant rates only, never genotypes).

4. **The corroboration, ATTRIBUTED.** The region-1 2×2 showing occluder carriers
   ~100% missing at the partner (`fAmB = 1.0` in 5 of 6 pairs) is **Seth's
   reported figure from the banked courier; it is not independently recorded
   anywhere else in this repo.** Say that in those terms. Do not write it as a
   measurement of ours.

5. **The timing fact, with its premises marked MEASURED.**
   - `plink --missing` / `.lmiss` is **NOT** currently emitted by the fire —
     measured 2026-08-18: zero `--missing`/`lmiss` hits under `src/`, and
     `aou_ld_panel.build_plink_ld_command` builds the square-mode argv as
     `--r square bin4 --keep-allele-order --mac 1 --nonfounders --write-snplist`
     over `--chr/--from-bp/--to-bp`.
   - That is **fine and blocks nothing**: the missingness is computable later in a
     cheap VM session from the same bfile (`/home/jupyter/afr_cohort`), which the
     n1-standard-32 holds and which the runbooks **STOP** rather than delete.
   - ⚠ **State the honest caveat:** no runbook step *commits* to preserving that
     VM after STEP G, and an AoU env on a STANDARD disk loses its disk on delete.
     So the premise is *"survives as long as the env is not deleted"*, not
     *"guaranteed available"*. If the env is ever deleted, `.lmiss` costs a bfile
     rebuild, not a re-fire of the LD panel.
   - **Therefore NO producer change is made now.** Cite the freeze-economy rule
     explicitly: adding `--missing` to the producer would put new behaviour on the
     $385–1,084 fire path to buy a post-fire diagnostic. That trade is refused.

6. **⚠ SETH'S TWO CONSTRAINTS — PRESERVE VERBATIM.** These bind *only if* someone
   later builds the cross-cohort version anyway. Reproduce both sentences word for
   word (quote them; do not paraphrase, do not compress, do not "improve" them):

   > 1. Join on (CHR, POS) only, per snp_id_bridge.R — and note the panel is
   >    GRCh38 while the sumstats are GRCh37, so the lift-over is part of the key.
   >    Do NOT add alleles to the key: this is the E-2 orientation exposure, and a
   >    chr:pos:REF:ALT key silently drops flipped records.
   > 2. Use MAF = min(EAF, 1-EAF), never EAF directly. I checked the arithmetic:
   >    EAF 0.014 and 0.986 both give MAF 0.0140, so MAF is invariant to which
   >    allele is called the effect allele — it is immune to the orientation flip
   >    that E-2 documents. Comparing raw EAF across the join would manufacture
   >    spurious "elevation" on every flipped record.

   Add one line of your own after them: *"That constraint pair is why the join is
   not to be built under time pressure — it is the exact surface E-2 is about."*
   Cross-reference the `E-2` item in this same file.

7. **The code state, stated so nobody re-litigates it.**
   `check_maf_depression` (`src/python/fire_verifier.py:632`) stays
   **implemented, tested, and DELIBERATELY UNWIRED**. This item does **not**
   authorise wiring it. Nothing was deleted; nothing was added.

8. **D-11 CONCURRENCE (record only).** Seth accepted all thirteen adjudications
   from `quick-260818-sml` with zero contested, and on D-11 explicitly requested
   **no change**: region-1 severity stays `FINDING` — the runbook wording already
   frames it as the finding, `exit_code` is non-zero either way, and nothing
   operational rides on the tier. **NO CODE WAS EDITED FOR D-11.** Say that
   sentence, so a future reader does not go looking for a commit.

9. **Cross-references:** the two runbook sites retargeted by this task
   (`260812-ox1-AGENT-PROMPT.md` STEP 9-GATE, `260812-ox1-BROWSER-PASTE.md` §9b);
   the `E-2` item; `R4-COVERAGE` (as a *sibling post-fire obligation*, referenced
   in prose only — **do not start a line with `## R4-COVERAGE`**).

⛔ **Forbidden anywhere in the appended text:** the strings
`nothing scientific is lost` and `nothing is lost` (either would flip guk R8/F10);
any line beginning with `## R4-COVERAGE`; any edit above the appended region.

**Step 2 — prove the append is append-only and the R4 block did not move.**

```bash
# G1 — ZERO deleted lines (deletions column must be 0)
git diff --numstat -- .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md

# G2 — the R4 block the live gate parses is unchanged modulo trailing whitespace
python3 - <<'PY'
import re, subprocess, hashlib
P = '.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md'
R4  = re.compile(r'^## R4-COVERAGE(?![-\w])', re.M)
SEC = re.compile(r'^## ', re.M)
def blk(t):
    m = R4.search(t)
    if m is None: return None
    n = SEC.search(t, m.end())
    return t[m.start():n.start()] if n else t[m.start():]
before = subprocess.run(['git','show',f'HEAD:{P}'], capture_output=True, text=True, check=True).stdout
after  = open(P, encoding='utf-8').read()
b, a = blk(before), blk(after)
assert b is not None, 'R4 heading missing BEFORE — wrong baseline'
assert a is not None, 'R4 heading DESTROYED by the append'
assert a.rstrip() == b.rstrip(), 'R4 BLOCK CONTENT CHANGED — the append leaked into the gate input'
nb = len([l for l in b.splitlines() if l.strip()])
na = len([l for l in a.splitlines() if l.strip()])
assert na == nb, f'R4 non-empty line count moved {nb} -> {na}'
print(f'G2 OK  R4 block preserved: {len(b.encode())} -> {len(a.encode())} B, {nb} non-empty lines, md5(rstrip) {hashlib.md5(b.rstrip().encode()).hexdigest()}')
PY

# G3 — the forbidden strings did not appear; the R8 pairing still holds
DI=.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
echo "nret=$(grep -ci 'nothing scientific is lost' $DI)  nretired=$(grep -i 'nothing scientific is lost' $DI | grep -c 'RETIRED')"   # must be equal and > 0
grep -c '^## R4-COVERAGE' $DI                                                                                                        # must be 1

# G4 — guk record output is byte-identical to the before-capture (NOT "exit 0" —
#      R3/R4 are pre-existing FAILs and must stay exactly as they were)
bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh record > "$S/guk-record.after.txt" 2>&1
diff "$S/guk-record.before.txt" "$S/guk-record.after.txt" && echo "G4 OK  guk record output diff EMPTY"
```

**Step 3 — NEGATIVE CONTROL for G2 (a green you have not seen fail is not
evidence).** In the **scratchpad only** — never on the repo file — copy
`deferred-items.md`, append a `# Deferred items — discovered during quick-260818-uoi
execution (2026-08-18)` banner *before* a `## ` heading, and re-run the G2 logic
against that copy. It **must FAIL** with `R4 BLOCK CONTENT CHANGED` (or the line-count
assertion). Paste the verbatim red into the SUMMARY. If it comes back green, G2 is
not measuring what it claims and you must stop and report rather than proceed.

**Step 4 — commit, explicit path only** (never `git add .` / `-A` on this GPFS tree):

```bash
git add .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
git commit -m "docs(quick-260818-uoi): register MISS-1 — MAF-depression follow-up redirected to a within-panel missingness test; D-11 concurrence recorded"
```

**GPFS contingency.** If the commit dies with `invalid object … Error building
trees`, run the guarded recovery loop, then retry the commit **once**:

```bash
git ls-files -s | awk '{print $2}' | while read -r h; do
  git cat-file -e "$h" 2>/dev/null || echo "MISSING $h"
done
# for each MISSING blob whose working-tree file exists and is unmodified:
#   git hash-object -w -- <path>
```
Re-hash **only** blobs whose working-tree file is present; if a missing blob has
no working-tree source, STOP and report — do not improvise a repair.
  </action>

  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && python3 - <<'PY'
import re, subprocess, sys
P='.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md'
R4=re.compile(r'^## R4-COVERAGE(?![-\w])',re.M); SEC=re.compile(r'^## ',re.M)
def blk(t):
    m=R4.search(t)
    if m is None: return None
    n=SEC.search(t,m.end()); return t[m.start():n.start()] if n else t[m.start():]
before=subprocess.run(['git','show','HEAD~1:'+P],capture_output=True,text=True).stdout
after=open(P,encoding='utf-8').read()
b,a=blk(before),blk(after)
assert b and a and a.rstrip()==b.rstrip(), 'R4 block moved'
assert '## MISS-1' in after, 'MISS-1 not registered'
nret=len([l for l in after.splitlines() if 'nothing scientific is lost' in l.lower()])
nrt =len([l for l in after.splitlines() if 'nothing scientific is lost' in l.lower() and 'RETIRED' in l])
assert nret>0 and nret==nrt, f'guk R8 pairing broken: {nret} vs {nrt}'
assert len(R4.findall(after))==1, f'R4 heading count != 1: {len(R4.findall(after))}'
d=subprocess.run(['git','diff','--numstat','HEAD~1','HEAD','--',P],capture_output=True,text=True).stdout.split()
assert d and d[1]=='0', f'deletions present: {d}'
print('PASS  MISS-1 registered append-only; R4 gate input byte-preserved; guk R8 pairing intact')
PY</automated>
  </verify>

  <done>
`deferred-items.md` carries exactly one new `## MISS-1` section containing all
nine required elements, Seth's two constraints verbatim; `git diff --numstat`
deletions == 0; the `_extract_r4_block` output is unchanged modulo trailing
whitespace; `guk record` output diff is empty (R8 still PASS, R3/R4 still their
pre-existing FAILs); the G2 negative control was OBSERVED RED; committed on one
explicit path.
  </done>
</task>

<task type="auto">
  <name>Task 2: Retarget the Stage-B MAF note in the two runbooks that carry it (+ optional HANDOFF clause), then close out</name>

  <files>
.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
.planning/HANDOFF.json
.planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SUMMARY.md
  </files>

  <action>
**Step 1 — re-confirm the measurement before you edit.** The note added by
quick-260818-sml appears in **2 of the 3** runbooks (measured 2026-08-18):

```bash
O=.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r
grep -n -i 'MAF\|improvise\|depression' $O/260812-ox1-AGENT-PROMPT.md $O/260812-ox1-BROWSER-PASTE.md $O/260812-ox1-READY-TO-FIRE.md
```

Expect hits in AGENT-PROMPT (~271–277) and BROWSER-PASTE (~371–377) and **zero**
in READY-TO-FIRE. If READY-TO-FIRE now has one, retarget it too. **If it still has
none, DO NOT ADD ONE** — adding new content to a third runbook is scope creep on a
frozen fire path, and the SUMMARY records the measured absence instead.

The two current blocks (verbatim at HEAD) are:

*AGENT-PROMPT, lines 271–277* — opens `NOTE (A-12, not wired — do not attempt it):`
and ends `…building it is Carter's planning-side work, not yours. Do not improvise it.`

*BROWSER-PASTE, lines 371–377* — opens `⚠ **NOT WIRED — do not improvise it (A-12).**`
and ends `…that join does not exist yet. Producing it is Carter's planning-side work, not the agent's.`

**Step 2 — capture the BEFORE for the enforcers.**

```bash
S="$SCRATCH"
bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all > "$S/vbu-all.before.txt" 2>&1
bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh all > "$S/guk-all.before.txt" 2>&1
```

**Step 3 — rewrite the two note blocks in place.** Keep each block's existing
position, indentation style and surrounding blank lines (AGENT-PROMPT is plain
text; BROWSER-PASTE uses markdown bold and backticks — match each host file). Each
rewritten note must say all four of:

1. `check_maf_depression` (A-12) remains **implemented, tested, and NOT WIRED** —
   unchanged by this task.
2. **The cross-cohort `(panel_maf, sumstats_maf)` join is NOT to be built.**
   Decided 2026-08-18 on Seth's recommendation; his courier is banked at
   `.planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SETH-COURIER-d-acceptance-as-received.md`.
   Replace the now-false sentence *"building it is Carter's planning-side work"* —
   it is **nobody's** work.
3. **The registered follow-up is `MISS-1` in
   `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`** — a
   **within-panel, post-fire** missingness test (per region, `F_MISS` of
   occlusion-excluded variants vs the region's own `F_MISS` distribution). Name
   the item id literally: a browser agent must be able to grep `MISS-1`.
4. **Nothing here blocks or changes the fire.** No new flag, no producer change,
   no extra command at Stage B. If a red or a question arises: paste and wait —
   **do not improvise** (the one clause worth keeping from the old text).

⛔ **Hard edit constraints:**
- Every changed line must lie **OUTSIDE** the pinned card ranges: AGENT-PROMPT
  **106–163**, BROWSER-PASTE **107–179**, READY-TO-FIRE **116–200**.
- Do not write `nothing scientific is lost` or `nothing is lost` (guk F10).
- Do not introduce any 20+ character hex run (vbu V3 constrains hex-run lengths
  inside the card block; keep new hex out of these files entirely).
- Append-only is NOT required here — this is a rewrite in place — but the diff must
  be confined to those two blocks. Nothing else in either file may change.

**Step 4 — prove the enforcers are unmoved.**

```bash
bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all > "$S/vbu-all.after.txt" 2>&1
diff "$S/vbu-all.before.txt" "$S/vbu-all.after.txt" && echo "OK  vbu all output diff EMPTY (expect 20 PASS / exit 0)"

bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh all > "$S/guk-all.after.txt" 2>&1
diff "$S/guk-all.before.txt" "$S/guk-all.after.txt" && echo "OK  guk all output diff EMPTY (R3/R4 stay their pre-existing FAILs)"

# the pinned card blocks are byte-identical (independent of the enforcer's verdict)
O=.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r
blk(){ awk -v s="$2" -v e="$3" 'BEGIN{p=0} (p && $0 ~ e){exit} ($0 ~ s){p=1} p{print}' "$1"; }
for spec in "$O/260812-ox1-AGENT-PROMPT.md|^STEP 6b|^STEP 7" "$O/260812-ox1-BROWSER-PASTE.md|^## 6b|^## 7"; do
  IFS='|' read -r f s e <<<"$spec"
  a=$(blk "$f" "$s" "$e" | md5sum | cut -d' ' -f1)
  b=$(git show "HEAD:$f" | blk /dev/stdin "$s" "$e" | md5sum | cut -d' ' -f1)
  [ "$a" = "$b" ] && echo "OK  card block unchanged: $(basename "$f")" || { echo "FAIL card block MOVED: $f"; exit 1; }
done

# forbidden framing still absent across all three
cat $O/260812-ox1-AGENT-PROMPT.md $O/260812-ox1-BROWSER-PASTE.md $O/260812-ox1-READY-TO-FIRE.md \
  | grep -ci 'nothing scientific is lost\|nothing is lost'   # must print 0

# the retarget actually landed in both
grep -c 'MISS-1' $O/260812-ox1-AGENT-PROMPT.md $O/260812-ox1-BROWSER-PASTE.md   # each >= 1
```

**NEGATIVE CONTROL for the card-block guard:** in the scratchpad, copy
AGENT-PROMPT, delete one line from inside `STEP 6b`…`STEP 7`, and run the same
`blk`+`md5sum` comparison against `git show HEAD:` — it must print `FAIL card block
MOVED`. Record the verbatim red in the SUMMARY. Never do this on the repo file.

**Step 5 — OPTIONAL, and only if steps 1–4 are entirely clean.** One clause on
`HANDOFF.json`. **Skip it if anything is awkward — the MISS-1 item plus the SUMMARY
already discharge the obligation, and `HANDOFF.json` is on three enforcer pins.**

If you do it:
- Append the clause to **`gates.producer_pre_fire_gates` ONLY**. ⛔ Do **not** touch
  `status` (guk R3), `resume_on_reconnect[0]` (guk R4, md5-pinned), or
  `gates.trsx5_posted_body` (guk R2, currently PASS).
- Clause content: the MAF-depression follow-up is **redirected** — the cross-cohort
  join is not to be built (Seth 2026-08-18); the registered item is **MISS-1** in
  `deferred-items.md`; `check_maf_depression` stays unwired.
- **Byte round-trip recipe, mandatory** (MEASURED true at plan time — 75,604 B, no
  trailing newline):

```bash
python3 - <<'PY'
import json
P='.planning/HANDOFF.json'
raw=open(P,encoding='utf-8').read()
d=json.loads(raw)
assert json.dumps(d, indent=2, ensure_ascii=False) == raw, \
    'round-trip is NOT byte-identical at HEAD — ABORT the optional edit, do not write'
d['gates']['producer_pre_fire_gates'] += " ⟶ 2026-08-18 (quick-260818-uoi): the A-12 MAF-depression follow-up is REDIRECTED — the cross-cohort (panel_maf, sumstats_maf) join is NOT to be built (Seth 2026-08-18); the registered replacement is MISS-1 in .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md (within-panel F_MISS test, post-fire). check_maf_depression stays implemented-but-unwired."
open(P,'w',encoding='utf-8').write(json.dumps(d, indent=2, ensure_ascii=False))   # NO trailing newline
PY
python3 -c "import json;d=json.load(open('.planning/HANDOFF.json'));print('valid JSON,',len(d),'top-level keys')"
python3 -c "
import json;P='.planning/HANDOFF.json';raw=open(P,encoding='utf-8').read()
assert json.dumps(json.loads(raw),indent=2,ensure_ascii=False)==raw,'round-trip broken AFTER edit'
assert not raw.endswith(chr(10)),'a trailing newline was introduced'
print('post-edit round-trip byte-identical, no trailing newline')"
bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh record > "$S/guk-record.after2.txt" 2>&1
diff "$S/guk-record.before.txt" "$S/guk-record.after2.txt" && echo "OK  guk record output STILL byte-identical"
```
If any assertion trips, `git checkout -- .planning/HANDOFF.json` and skip step 5.
Record the skip and its reason in the SUMMARY — a declined optional edit is a
result, not a gap.

**Step 6 — write the SUMMARY** at
`.planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SUMMARY.md`.
It must carry:
- **What Seth accepted:** all 13 adjudications, zero contested; he reloaded his own
  prototype and reproduced three broken checks himself (D-02 prefix-vs-detail-in-status,
  D-02b the quiet non-`deferred` hole, D-09 the false positive on innocent `estimate`
  prose). Note which of his nine checks that is: 3 of 9.
- **D-11 CONCURRENCE — NO CODE CHANGED.** Region-1 severity stays `FINDING` at
  Seth's explicit request. State plainly that no file under `src/`, `tests/`,
  `config/` or any Snakefile was touched by this task, and that
  `git diff --stat` over those paths is empty.
- **The redirect + the item id `MISS-1`**, with the one-line rationale (the
  mechanism predicts callability, not MAF) and the two retargeted runbook sites.
- **The measured-premises table** (the four rows from `<interfaces>`), explicitly
  separating what we MEASURED from Seth's `fAmB = 1.0 in 5 of 6` claim, which is
  **his and not independently recorded in this repo**.
- **The guard transcript:** the before/after diffs (empty), the pinned-card md5
  equality, and the **verbatim red output of both negative controls**. A green
  without its observed red does not go in this section.
- **Not done / declined:** no `--missing` added to the producer (freeze economy);
  no note added to READY-TO-FIRE (it never carried one — measured); step 5 taken
  or skipped, with the reason.

**Step 7 — commit, explicit paths only.**

```bash
git add .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md \
        .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md \
        .planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SUMMARY.md \
        .planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SETH-COURIER-d-acceptance-as-received.md \
        .planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-PLAN.md
# add .planning/HANDOFF.json ONLY if step 5 was completed and every guard was clean
git commit -m "docs(quick-260818-uoi): retarget the Stage-B MAF note to MISS-1; bank Seth's D-01..D-13 acceptance courier"
```

⛔ Never `git add .` or `git add -A` on this shared GPFS tree. Never stage
`tests/m3/sparse_parent_benchmark.tsv`. **Do not push** — that is the
orchestrator's. Same GPFS `invalid object` contingency as Task 1: guarded
`hash-object -w` recovery loop, retry once, then stop and report.
  </action>

  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all && O=.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r && grep -q 'MISS-1' $O/260812-ox1-AGENT-PROMPT.md && grep -q 'MISS-1' $O/260812-ox1-BROWSER-PASTE.md && [ "$(cat $O/260812-ox1-AGENT-PROMPT.md $O/260812-ox1-BROWSER-PASTE.md $O/260812-ox1-READY-TO-FIRE.md | grep -ci 'nothing scientific is lost\|nothing is lost')" = "0" ] && [ -z "$(git diff --stat HEAD~2 HEAD -- src/ tests/ config/ '*.smk' Snakefile)" ] && python3 -c "import json,sys;P='.planning/HANDOFF.json';raw=open(P,encoding='utf-8').read();d=json.loads(raw);assert json.dumps(d,indent=2,ensure_ascii=False)==raw;assert not raw.endswith(chr(10));print('HANDOFF.json round-trip intact')" && echo "PASS  runbooks retargeted to MISS-1; vbu green (20 PASS); zero code changes; HANDOFF byte-clean"</automated>
  </verify>

  <done>
Both runbooks that carried the A-12 note now name `MISS-1` and state the
cross-cohort join is not to be built; READY-TO-FIRE is unchanged (measured: it
never carried the note); every pinned card block is byte-identical and
`260817-vbu-verify.sh all` prints the same 20 PASS / exit 0 as before; `guk all`
output diff is empty; `git diff --stat` over `src/`, `tests/`, `config/`,
Snakefiles is EMPTY; `HANDOFF.json` either untouched or round-trip byte-clean
with `guk record` unmoved; SUMMARY written with both negative controls' verbatim
red; committed on explicit paths, unpushed.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| plan text → executor edits → **live gate inputs** | `deferred-items.md` and the three ox1 runbooks are parsed at runtime by `fire_verifier.check_coverage_disclosure_resolved`, `260817-vbu-verify.sh` and `260814-guk-verify.sh`. A prose edit here is an input change to a gate that stands between Carter and a $385–1,084 irreversible spend. |
| chat-sourced courier → repo record | Seth's body is an AS-RECEIVED transcription with **no byte anchors supplied** (stated in its own provenance header). It cannot be verified against a digest. |
| repo record → future implementer | Whatever MISS-1 says is what someone builds months from now, without Seth in the room. |

No network, no untrusted user input, no credentials, no perimeter contact: the
usual S/I/D/E surfaces are absent. The live risks are **Tampering (accidental)**
and **Repudiation (unattributed claims)**.

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-uoi-01 | Tampering | `deferred-items.md` R4-COVERAGE block (parsed by `_extract_r4_block`) | mitigate | Append must begin with `^## ` so the extractor terminates at today's boundary; G2 compares `_extract_r4_block(git show HEAD:…)` to the post-edit block and asserts equality modulo trailing whitespace; the **`# `-banner negative control must be OBSERVED RED** before G2 counts as evidence. |
| T-uoi-02 | Tampering | the STEP 6b/`## 6b` trsx5 card blocks in all three runbooks | mitigate | Task 2 edits are confined to measured lines 271–277 / 371–377, far outside the pinned 106–163 / 107–179 / 116–200 ranges; guarded by an `md5sum` equality on the extracted card block vs `git show HEAD:` **and** by a byte-identical `260817-vbu-verify.sh all` output diff; delete-a-line negative control required. |
| T-uoi-03 | Tampering | `260814-guk-verify.sh` R8 / F10 string invariants | mitigate | `nothing scientific is lost` / `nothing is lost` are declared forbidden strings in both task actions; verified by an explicit `grep -c` (must be 0 across the runbooks) and by the R8 nret==nretired pairing check on `deferred-items.md`. |
| T-uoi-04 | Tampering | `HANDOFF.json` byte format (75,604 B, no trailing newline, 3 enforcer-pinned keys) | mitigate | Step 5 is OPTIONAL and abortable; the pre-edit assertion refuses to write unless the round-trip is already byte-identical; only `gates.producer_pre_fire_gates` may be touched; post-edit round-trip + no-trailing-newline + `guk record` output-diff all re-asserted; failure ⇒ `git checkout --` and skip. |
| T-uoi-05 | Repudiation | the `fAmB = 1.0 in 5 of 6 pairs` corroboration | mitigate | MEASURED at plan time: `fAmB` occurs **only** in Seth's banked courier, nowhere else in-repo. MISS-1 and the SUMMARY must attribute it to him as an unverified-by-us claim. Asserting it as our measurement is the exact "aggregate agreement hides component errors" failure mode. |
| T-uoi-06 | Repudiation | the "VM + bfile persist post-fire" premise | mitigate | The record supports STOPPED-not-deleted but **no runbook step commits to it after STEP G**, and a STANDARD-disk env loses its disk on delete. MISS-1 must state the premise as conditional, not guaranteed, and name the fallback cost (a bfile rebuild, not an LD re-fire). |
| T-uoi-07 | Elevation of Privilege | scope creep from a records task into the frozen fire path | mitigate | Plan-level prohibition: no `src/`, `tests/`, `config/`, Snakefile edits; `check_maf_depression` explicitly not wired; no `--missing` added to the producer (freeze-economy rule stated in the item itself); Task 2's automated verify asserts `git diff --stat HEAD~2 HEAD -- src/ tests/ config/ *.smk Snakefile` is **empty**. |
| T-uoi-08 | Information Disclosure | the future missingness test's egress surface | accept | The registered test is specified as per-variant/region **aggregate rates only**, single-cohort, computed in-perimeter — no genotypes, no individual-level data. Nothing is computed by this task; the constraint is recorded for whoever implements it. |
| T-uoi-09 | Denial of Service | — | accept | No runtime component; a records task cannot degrade availability. |
</threat_model>

<verification>
Run from the repo root after both tasks:

```bash
# 1. the live R4 gate input is unmoved and MISS-1 exists
python3 - <<'PY'
import re
P='.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md'
t=open(P,encoding='utf-8').read()
R4=re.compile(r'^## R4-COVERAGE(?![-\w])',re.M); SEC=re.compile(r'^## ',re.M)
m=R4.search(t); n=SEC.search(t,m.end())
blk=t[m.start():n.start()] if n else t[m.start():]
print('R4 non-empty lines:',len([l for l in blk.splitlines() if l.strip()]),'(was 41)')
print('R4 terminator     :','EOF' if n is None else t[n.start():n.start()+20].strip())
print('MISS-1 present    :','## MISS-1' in t)
PY

# 2. the trsx5 enforcer is still green (20 PASS, exit 0)
bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all; echo "vbu exit=$?"

# 3. the guk record section is UNMOVED (R8 PASS; R3/R4 stay their pre-existing FAILs)
bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh record

# 4. ZERO code touched by this quick task
git diff --stat HEAD~2 HEAD -- src/ tests/ config/ '*.smk' Snakefile    # must be empty

# 5. append-only over deferred-items.md
git diff --numstat HEAD~2 HEAD -- .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md   # deletions column == 0

# 6. nothing unpushed-but-unstaged got swept in
git status --porcelain
```
  </verification>

<success_criteria>
- [ ] `deferred-items.md` gained exactly one `## MISS-1` section, appended, deletions == 0.
- [ ] `_extract_r4_block` output is byte-identical modulo trailing whitespace (41 non-empty lines, unchanged content) — with the `# `-banner negative control **observed RED**.
- [ ] MISS-1 carries: the redirect + Seth's reasoning; the within-panel test spec (per-region `F_MISS` vs the region's own distribution, rank-based or >90th-percentile fraction); single-cohort + egress-safe rationale; the attributed `fAmB` corroboration; the `.lmiss`-not-emitted timing fact with its MEASURED premises and the honest VM-persistence caveat; **Seth's two constraints VERBATIM**; the unwired status of `check_maf_depression`; the D-11 concurrence with an explicit "no code changed"; cross-references.
- [ ] Both runbooks that carried the A-12 note name `MISS-1` and state the cross-cohort join is **not to be built**; READY-TO-FIRE untouched (measured: never carried one).
- [ ] Every pinned card block byte-identical; `260817-vbu-verify.sh all` output diff EMPTY (20 PASS / exit 0) — with the delete-a-line negative control **observed RED**.
- [ ] `260814-guk-verify.sh all` output diff EMPTY (R3/R4 remain pre-existing FAILs; F10 and R8 remain PASS).
- [ ] `git diff --stat` over `src/`, `tests/`, `config/`, Snakefiles is **EMPTY** — no code, no wiring, no `--missing` on the producer.
- [ ] `HANDOFF.json` either untouched or round-trip byte-identical with no trailing newline, only `gates.producer_pre_fire_gates` changed, `guk record` unmoved.
- [ ] SUMMARY written, including both negative controls' verbatim red and the declined/not-done list.
- [ ] Two commits on explicit paths with `docs(quick-260818-uoi): …` messages. **Not pushed.**
- [ ] No perimeter contact, no network, no fire.
</success_criteria>

<output>
After completion, create
`.planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SUMMARY.md`
per the Step 6 content list. Report to the orchestrator: the MISS-1 item id, both
retargeted runbook sites, the before/after enforcer diffs, whether the optional
HANDOFF clause was taken or declined (and why), and the two negative-control reds.
The orchestrator owns the STATE.md quick-task row and the push.
</output>
