# READY-TO-FIRE — m3-04c Task 3 (the ~11-day / $385–1,084 AoU native-plink LD fire)

> ## ⛔ AN AGENT MUST NEVER FIRE IT. (HANDOFF `do_not[0]`.)
>
> This runbook was **produced by an agent**. It was **verified at commit
> `5284505f5b7410fe3775e96f3ac3eb1adf668f40`** (the 260812-ox1 L-01 HEAD; any commits
> after that HEAD are `.planning`-only — 0 files under `src/`, `tests/`, `config/`,
> `Snakefile`). All **agent-verifiable rows are green as of 2026-08-12** per
> `260812-ox1-evidence.tsv` (20/20 PASS; suites 907/31/0 and 136/1/0). **The fire
> decision, and EVERY perimeter command below, are Carter's.** Every quoted perimeter
> command is copied character-for-character from the CORRECTED
> `260811-rcw-PRE-FIRE-GATE-REVIEW.md` (§4, the liveness-arbiter block, §5, and
> `## Corrections (2026-08-12)`) — never from the m3-04c PLAN or the blast radius
> (review §2.1(8): their pointers and commands drifted).

**Contents: ONLY Carter's remaining items, in fire order.** Everything an agent could
close is closed: PRE-FIRE 1 LANDED (commit `5284505`, per-region manifest upload, TDD),
PRE-FIRE 3 is settled code-side (item 8), the L-checks are re-anchored green.
⚠ **Item 6b was ADDED 2026-08-14** — the fire-blocking trsx5 byte check was missing from
this list while this line claimed the list was complete. Items 7–11 are **unrenumbered**;
cross-references to "item 7" elsewhere in the 260812-ox1 package still resolve.

---

## 1. Push/pull gate — origin == local at fire time

- From NCSU: `git push` (⚠ NOTE: `git push` does **NOT** push tags — push tags
  explicitly if any were created).
- In the Workbench: clone, then **`git checkout m3-W2-aou-deltas`** →
  **`git checkout -f`** (the Workbench Jupyter clean/smudge filter re-dirties
  notebooks on every git op; `-f` is the only clean switch) — the SKILL.md
  fresh-clone checklist. Confirm `git branch --show-current` prints
  `m3-W2-aou-deltas`. **Never run from `main`** (stale unrelated history; a
  clone-from-`main` re-run wedges deterministically).

## 2. §4 row 1 — bucket `.npz` count (expect **0** pre-fire)

PRIMARY (literal bucket):

```
gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l
```

Alternate, env-variable form — note where the quotes go:

```
gsutil ls "${WORKSPACE_BUCKET}/ld/AFR_aou/"*.npz | wc -l
```

⚠⚠ **Never-prefix rule (paraphrased on purpose; the broken form is deliberately NOT
reproduced in this document):** `WORKSPACE_BUCKET` **already carries the scheme** —
`echo $WORKSPACE_BUCKET` must print `gs://rw-migration-aou-rw-476cdac2` (SKILL.md:43).
Writing the scheme AGAIN in front of the variable doubles it; gsutil then writes a
usage error to **stderr**, prints **nothing** to stdout, and the piped count prints
**0**. That zero **FALSE-PASSES this very row** pre-fire, and during STEP B it reads a
**healthy fire as dead**. Same defect class the project fixed in quick-260611-tbw (gap
C3). If a poll ever returns 0 unexpectedly, re-run the literal-bucket form and check
stderr (which `| wc -l` discards) before concluding anything.

Expected: **0** pre-fire. **Anything > 0 means a prior fire banked regions** —
reconcile before re-firing (`force_fresh=False` on resume; the `.npz`, not the panel
TSV, gates the resume skip).

## 3. §4 row 2 — VM state (UI only)

Read the **AoU environment panel** in the Workbench UI (do not shell out). Expected:
environment **present, STOPPED, disk intact** (`n1-standard-32`, holds
`/home/jupyter/afr_cohort`). ⚠ **Read the DISK-TYPE label before ANY destructive env
action** — an env on a STANDARD disk loses everything on delete; the project rule is
**Reattachable persistent disk**.

## 4. §4 row 3 — the stale panel TSV (PRE-FIRE 2; zero risk, zero compute cost)

```
gsutil stat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv
```

If present:

```
gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv | head -1
```

Expected header: **9 tab-separated columns** with `n_dropped_occluded` at index **7**
(0-based; re-derived with `ast` in the rcw log block CONTEXT-C — a naive comma-split
on the source is WRONG). If the header does not match, **`gsutil rm` it** (same URI as
above — it is rebuilt from the banked per-region `.npz`, so deleting it costs no
compute; a stale 7/8-column TSV would abort the fire after ~2 regions of compute).
⚠ **"0/276 banked" does NOT evidence the TSV's absence** — prior fires appended
`status=error` rows unconditionally.

## 5. §4 row 5 — cohort-MT data-layer re-verify (mutable state the fire READS)

```
gsutil du -s gs://rw-migration-aou-rw-476cdac2/ld/mt_AFR_qc.mt/entries/rows/parts/
```

**AND** `count_cols()` / `count_rows()` off the MT itself. Expected: `du` **≫ 1 GB**
and non-zero cols/rows. ⚠ The canonical MT path has **NO `/mt/` subdirectory** — a
wrong `…/ld/mt/…` path mimics the empty-final catastrophe. ⚠ **A `_SUCCESS` marker is
NOT evidence of data** (the 2026-05-21 $2,100 and 2026-06-10 catastrophes both passed
a `_SUCCESS` check over 0 bytes). Firing ~263 VM-h against an emptied MT is that
failure mode with a bigger bill.

## 6. GATE 1 — cost/credit eyeball

Read the **live balance in the Workbench billing panel** before the $385–1,084 commit.
(The CDR-pin half needs NO re-verification: `_resolve_aux_base` makes v8→v9 a path
no-op.)

⚠ **NO CREDIT BACKSTOP behind this gate** (`DEC-2026-08-16-aou-credit-request-denied`):
AoU support has ruled that compute charges from user-run analyses are **not
refundable** — final. An overrun past this gate is unrecoverable, not reimbursable,
so **Stage B's measured extrapolation is what must carry the Stage-C go/no-go.**

## 6b. THE trsx5 BYTE CHECK — GATES THE FIRE (added 2026-08-14, Seth escalation; ADJUDICATED-RESOLVED 2026-08-17)

⛔ **This gate BLOCKS THE FIRE.** trsx5 IS the pre-registration the fire executes;
a posted body that has CHANGED since adjudication is unanswerable after output is
banked. (It no longer blocks obligation-(2) posting — that is freed by
`DEC-2026-08-17-trsx5-gate-released` but still deferred to manuscript submission
day per `DEC-2026-08-12-e2-p1-closing-sentence`.)

**1 — download.** In a logged-in OSF browser tab, download
https://osf.io/az52u/files/trsx5 — the **file**, not the page. Then:

```
wc -c   <the downloaded file>
md5sum  <the downloaded file>
```

Report **both, verbatim**, whatever they say.

**2 — ⚠ ADJUDICATE ON THE BYTE COUNT FIRST. Expected: 9,695 bytes.** A byte
count cannot be mistranscribed into a false pass; a hash can. **ANY other size is
a STOP by itself** — no hash comparison is required, and none may overrule it.
Another size means **the posted record has CHANGED** since the 2026-08-17
adjudication, and the fire is **HELD** until that is explained and recorded.
⚠ **9,758 or 9,907 observed at download time is NOW ITSELF A STOP**, not a pass —
those two were the expectations of the **SUPERSEDED** two-body card.

**3 — the hashes then confirm:**

| Observed | md5 | Meaning | Action |
|---|---|---|---|
| **9,695 B** | `c19be8b2ad7cd6a45fee1d668d8a9cf9` | the adjudicated posted body | **gate PASSES** — proceed |
| 9,695 B | anything else | same size, different content — its own anomaly | **STOP**; report verbatim |
| any other size | — | the posted record changed since the 2026-08-17 adjudication | **STOP** — the fire is **HELD** until it is explained and recorded |

Optional second confirm on the 9,695-B body:
`sha256 1ba83e4e633cd11c7f0896969cd6a419dada7b442365a5a0a3ea7307a342aab4`

**4 — `ADJUDICATED-RESOLVED 2026-08-17`**, per
`DEC-2026-08-17-trsx5-gate-released`. The 9,695-B body is the **verified
byte-exact plain-text rendering of the COMPLETE 9,907-B lineage** — a 6-step
transform (strip bold / italic / backticks / bullet markers, blank-line re-flow,
no trailing newline; net **−212 B**, every byte assigned). **Replicated
firsthand** from the git object store at `3684413`, implemented from Seth's prose
spec alone, **first attempt, no fitting** — and the md5 it lands on is the one
**Carter measured himself** on his authenticated OSF download at this very gate on
2026-08-16, which is what makes this a closed chain rather than a claim about
someone else's file. ⚠ `c19be8b2ad7cd6a45fee1d668d8a9cf9` is **NO LONGER
"advisory, Seth-reported, unverified"** — it is a **VERIFIED anchor**, measured
independently on both sides. **The old `{9,758, 9,907}` two-body card is
SUPERSEDED.**

**5 — HISTORICAL REFERENCE, keep — neither is a live pass condition any more.**

| Historical anchor | md5 | What it is now |
|---|---|---|
| 9,758 B | `28ecdb3160833da80cfa25952f76415b` | the repo-canonical paste block — **historical reference only** |
| 9,907 B | `425d925a88ab474ec2396cbea25e665c` | the methodologist's complete lineage — retained as the **source-of-rendering** anchor for the 9,695-B body |

**Provenance of the 9,758 anchor** — re-derived firsthand 2026-08-14 on the
working tree **and** at `ac4c990`, both identical; the extraction **excludes**
both marker lines:

```
F=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md
awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | wc -c
awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | md5sum
```

⚠ **Report the bytes and the md5 verbatim either way.** The ledger's trsx5 entry
is **append-only**: it now carries three dated sub-entries
(`BYTE-LEVEL-CONTESTED 2026-08-13`, `CORRECTED 2026-08-14`,
`RESOLVED 2026-08-17`) and the falsified readings stay visible.

> **Why a third copy of this card exists despite the drift risk** (the card also
> lives in `260812-ox1-AGENT-PROMPT.md` STEP 6b and `260812-ox1-BROWSER-PASTE.md`
> §6b): the size-first design removes the false-pass mode that made duplicate
> copies dangerous — a mistranscribed hash can no longer produce a PASS, because
> the byte count adjudicates first. Against that, a fire-blocking gate **absent
> from Carter's only checklist** is the divergence class `DEC-2026-08-12`
> consolidated against. All three copies are checked mechanically by
> `.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh`
> (V0-V7, every check seen red through its own shipped sub-mode). The older
> `260814-guk-verify.sh fire` section enforced the **superseded** two-body card;
> a RED there against this card is **expected and is not a defect**.

## 7. PRE-FIRE 1b — the recorded branch decision (sign BEFORE STEP B; re-read at STEP E)

**PRE-FIRE 1 LANDED** in this task (commit `5284505`: per-region
`{region_id}.occlusion_manifest.tsv` written beside the shared manifest and uploaded
inside the existing `if ok:` block alongside the excludelist; TDD, 5 tests, suites
green). **Branch (i) is therefore the default.**

> ### PRE-FIRE 1b DECISION RECORD (Carter's signature — an agent may not fill the last two lines)
>
> Chosen branch: **(i) — PRE-FIRE 1 landed; expect every occluded region to bank a
> per-region manifest.** Both refusal flags stay `false`
> (`allow_partial_manifest` code-default False at `assemble_occlusion_catalog.py:345`;
> `occlusion_lockstep.allow_degraded: false` at `config/pipeline.yaml:295` — both
> re-verified green in L-10, 2026-08-12). The catalog is stamped `stage_a_manifest`;
> nothing else changes.
>
> **Branch-(ii) re-entry instruction — RE-READ THIS AT STEP E:** branch (ii) is
> **diagnosable only post-fire** — the per-region append is BEST-EFFORT
> (`run_native_ld_panel` continues on any manifest exception while still writing the
> excludelist), so GATE 1 (`allow_partial_manifest`) can still fire even under (i).
> If it does: supply the missing manifests if recoverable; only if not, set
> `allow_partial_manifest: true` explicitly and record which regions are knowingly
> omitted (`n_regions_excludelist_only`). Under (ii) the stamp **stays
> `stage_a_manifest`**. `excludelist_degraded` + `allow_degraded: true` belongs to
> **branch (iii) ONLY** (review §2.1(9) — read PLAN `:1508`'s "(ii)" as a typo).
>
> Date: August 14, 2026  Signature: Carter Clinton

## 8. PRE-FIRE 3 — the gated real-`.bim` validation (settled code-side; ONE in-perimeter action)

Carter's in-perimeter action: place the real region-1 window `.bim` at
`data/aou/region1_window.bim` **in the repo clone**, then run the gated test **by
name**:

```
pytest "tests/m3/test_occlusion_span_filter.py::test_region1_real_window_known_answer_gated" -rs -q
```

⚠ **MANUAL LINE-NUMBER COMPARISON IS FORBIDDEN.** The §4-row-4 off-by-one risk lives
ONLY there (editor/awk/sed line numbers are 1-based; the oracle is 0-based). The gated
test computes BOTH sides in the same 0-based `enumerate` space
(`test_occlusion_span_filter.py:520` vs the `:186` oracle constant), so it **CANNOT
false-pass on an origin error** — a mis-based oracle fails loudly as a uniformly
±1-shifted set. The source doc's base is unrecoverable (adjacency language is
base-invariant; 260812-ox1 evidence log, CONTEXT-P3b) — the gated test IS the
instrument. Interpretation:

| Outcome | Meaning | Action |
|---|---|---|
| PASS | origin settled (0-based); **PRE-FIRE 3 CLOSED** | proceed |
| FAIL, observed set == expected shifted uniformly ±1 | the oracle's base was off by one | report; a one-line constant fix in the TEST file (not freeze-gated) + re-run; do **NOT** touch `occlusion_span_filter.py` (frozen) |
| any other FAIL | detector/window mismatch — a real finding | **STOP; do not fire; report** |

## 9. STEP A — region-1 re-run gate (the gate immediately before the money)

Re-run **region 1 ONLY**. **PASS** = `.npz` count 0 → 1; panel `status == ok`; `n_var`
slightly under 102,421; `n_dropped_occluded` ≈ 5 logged; no "not symmetric", no
"Killed", no dmesg OOM. **FAIL → stop and report; do not proceed to 276.**

**MECHANICAL GATE for this stage (added 2026-08-18, `quick-260818-sml`):**
`src/python/fire_verifier.py stage-a` — it re-reads the BANKED `.npz` through the
SHIPPED `content_verify_npz`, checks the manifest at the data layer (count, field
parseability AND `region_id` on every record row), evaluates the clause-(d)
occlusion ceiling from the panel TSV, and asserts region 1's status is exactly
`ok`. **`git pull` on the VM first; exit 0 is required to proceed.** Full
invocation in `AGENT-PROMPT` STEP 8-GATE / `BROWSER-PASTE` §9. ⚠ The re-read loads
a ~42 GB dense array and takes many minutes — that is not a hang.

**SH2B3 `__sub14` follow-up (MEDIUM-6):** once `m2_region_00040__sub14` is banked, run
one AFR `run_finemap` at `SH2B3_12q24` and read the `estimate_s` log line (it prints
`ld_matrix` = the path OPENED and `ld_file_declared` = the path DECLARED). **If
`ld_matrix` reads `identity`, the coverage gate rejected the panel**
(`run_susie_rss.R:500`, thresholds 50 / 0.5 loaded at `:716-718`) — report it with the
observed `ld_overlap` / `ld_overlap_fraction`; do not paper over it. The three honest
remedies — select `__sub15` instead, use the STITCHED parent `m2_region_00040` if one
is built, or lower `min_ld_coverage` — are **scientific calls, not executor calls**.

## 10. STEP B — THE FIRE (~263 VM-h, ~11 days, $385–1,084)

`nohup` plus `timeout 312h` (13-day wall-cap), **server-side**, on the
STOPPED-not-deleted Cloud Analysis VM. **Do NOT restart the kernel.** Check in every
**2–3 days**. **Teardown is UI-only** (the pet SA is list-only; `timeout` is the
backstop).

**MECHANICAL GATES for this stage (added 2026-08-18, `quick-260818-sml`):**
`src/python/fire_verifier.py stage-b` before the fire (per-region peak-RAM
headroom on the 120 GiB VM + the cost-per-BANKABLE-region denominator) and
`… stage-c` at EVERY 2–3-day check-in (the status rollup, with `deferred_*` rows
PASSING as the gates working, `verify_failed`/`error:` rows failing at FINDING,
and an unrecognized status a HARD_STOP). **Exit 0 is required to proceed; a red is
a STOP, never a licence to retry or repair.** Full invocations in `AGENT-PROMPT`
STEP 9-GATE / STEP 10 and `BROWSER-PASTE` §9b / §9c.

**Liveness is the GCS `.npz` object listing climbing toward 276 — NOT the kernel
light, NOT a `_SUCCESS` marker, NOT the log.** THE POLL COMMAND, both corrected forms:

```
gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l
```

```
gsutil ls "${WORKSPACE_BUCKET}/ld/AFR_aou/"*.npz | wc -l
```

⚠⚠ The never-prefix rule of item 2 applies verbatim here (paraphrase only in this
document): the variable already carries the scheme; doubling it empties stdout and a
**healthy fire reads as dead**. On any surprising 0: literal-bucket form + read stderr
first.

⚠ **276 IS NOT A PASS BAR.** A `verify_failed` region **never uploads** (the
`if ok:` gate; the file stays in scratch), and a per-region exception is recorded as
`status="error: …"` while **the loop continues**. A final count under 276 is a
**partial bank — a real, reportable outcome** to report with its per-region statuses,
not a failure to paper over and not a reason to re-fire blindly (`force_fresh=False`
on resume). **A count that stops climbing is the signal to investigate**, not a number
to wait out.

**Deferral vocabulary (added 2026-08-13, commit d9fbc63 — both producer gates
landed):** in the panel TSV, `deferred_infeasible_square` (n_var above the
`--max-n-var` ceiling, default 120000 = the consumer's `m3_convert_max_n_var`)
and `deferred_occlusion_anomaly` (trsx5 clause (d), occluded count > 0.0005 ×
n_var, defer-not-exclude) rows are **THE GATES WORKING** — expected for ~29+
regions above the ceiling. The bankable target is **276 minus deferrals**; no
deferral count is a pre-committed expectation (the count emerges at fire time).
The monitoring rollup reports the four status classes SEPARATELY: `ok` /
`deferred_infeasible_square` / `deferred_occlusion_anomaly` / `error`.

**Clause-(d) ceiling figures (per Seth's 2026-08-14 review):** the anomaly
threshold is **`0.0005 × n_var`** with a **STRICT `>`** — a region defers only when
its occluded count strictly **exceeds** the threshold. At the pinned **120,000**
cap that is **60.0** variants; at region 1's `n_var` of **102,421** it is **51.2**.
Region 1's expected **~5** occlusions sit roughly **10× under** the ceiling, so a
deferral there would itself be the finding.

**Post-fire disclosure duty (note only — not implemented here).** Per clause (d)
the measured deferral list is disclosed as a deviation at STEP E/F time — **and,
per Seth's 2026-08-14 R4, that is not sufficient on its own.** The square-mode
deferral set is ALSO a **methods/limitations** disclosure: an ancestry-specific
**COVERAGE GAP**, not merely an internal deferral status. Disclose it alongside
the occlusion disclosure in the form *"N regions exceeding n_var X were not
converted in square mode; affected span M Mb"*, using the **ACTUAL post-fire
numbers** from the panel TSV's `deferred_infeasible_square` rows. Record the
**remedy path** so the gap reads as bounded, not permanent: the frozen producer
already supports **banded mode** (`--r gz` with an `--ld-window-*` bound), and
large regions can be split into **overlapping sub-windows** — **NEITHER happens
before this fire.** Registered as **`R4-COVERAGE`** in
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`.
**NAMED ENFORCER (added 2026-08-18, `quick-260818-sml`):** the obligation is no
longer belief-only. `fire_verifier.check_coverage_disclosure_resolved` reads that
file and FAILS while the pre-fire estimate sentinels are still in it, or if the
warning is deleted without a `MEASURED:` provenance line, or if the heading is
renamed (an empty block is vacuous, not green). `python3
src/python/fire_verifier.py disclosure --file <that file>` exits **1 today, by
design**. Its pytest,
`tests/m3/test_fire_verifier.py::test_coverage_disclosure_live_gate_against_the_repo_file`,
SKIPS while no measured `m3-W2-native-plink-panel.tsv` exists in-repo and goes RED
the moment one lands — which is why the pinned `tests/m3` skip count moved 31 → 32.
⚠ **The "no-loss" framing for these deferrals is RETIRED — do not reintroduce it
here.** It is true of this pipeline as currently built and FALSE as a statement
about the science. The exact retired wording, and why, is quoted once and only
once in the `R4-COVERAGE` entry; `260814-guk-verify.sh fire` asserts it appears
ZERO times across all three runbook files, so restating it here would fail the
checker by design.

## 11. STEP C/D/E/F/G — one line each (full text lives in review §5)

- **C — size/plan the egress:** `gsutil ls -l` over the banked `.npz` →
  `plan_ld_egress.py` → `m3_egress_plan_AFR.tsv`; expect ≤ 22 chromosome groups plus
  size splits; ⚠ confirm the REAL AoU egress threshold on the FIRST request (50 GB is
  OUR working ceiling, not AoU's documented cap). ⚠ **The egress plan and its
  size/cost extrapolation cover the BANKED (square-feasible) set, not 276** —
  read every per-region figure here as **cost-per-bankable-region, never
  cost-per-region-of-276** (relabelled 2026-08-14 per Seth's review); the regions
  above the `--max-n-var` ceiling defer, produce no `.npz`, and egress nothing.
- **D — egress per group:** per-group AoU egress review → `gsutil -m cp` into
  `data/interim/aou_ld_exports/AFR_aou/`; ALSO fetch the excludelists, `.afreq`
  sidecars, the panel TSV, **and the per-region occlusion manifests (PRE-FIRE 1
  landed — post-fire the bucket holds one per occluded region that PASSED verify;
  zero-occlusion and verify-failed regions have none, by design)**; audit-log row + SHA-256 sub-manifest per
  group; commit token `(m3-04c-T3-chr{N}-AFR)`.
- **E — hand back to the DAG:** re-run m3-04b's catalog rule **under the branch
  RECORDED at item 7 (re-read the 1b template NOW — branch (ii) is diagnosable only
  post-fire)**; then ingest flags + the 575-job convert DAG (only the
  BLOCKER-D-convertible subset converts).
- **F — OSF amendment-update (Check-2 redefinition):** agent DRAFTS, **Carter POSTS**
  to osf.io/az52u, GUID recorded in-repo; no redefined check may be cited as PASSED
  before that record exists.
- **G — end-to-end read-path proof on real data:** one AFR `run_finemap` on a curated
  region with an M2 counterpart; its output JSON must show `ld_file_declared` ==
  `ld_matrix` == the `AFR_aou/…rds` path — never `identity`/`identity_fallback`,
  never an `AFR/…` 1kG path.

---

*End of runbook. Everything above items 1–11 that could be closed from NC State at $0
has been closed and evidenced in `260812-ox1-evidence.log` / `.tsv`. What remains is
Carter's alone. **AN AGENT MUST NEVER FIRE IT.***
