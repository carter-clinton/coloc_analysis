# BROWSER-PASTE SEQUENCE — m3-04c Task 3 fire (companion to 260812-ox1-READY-TO-FIRE.md)

> ⛔ **AN AGENT MUST NEVER FIRE IT. Every command below is for CARTER to paste in the
> AoU Workbench browser session.** This file renders the READY-TO-FIRE runbook into
> paste-ready blocks. Provenance discipline: each block is either **[RUNBOOK]**
> (byte-quoted from the runbook / corrected rcw review) or **[DERIVED @HEAD]**
> (constructed 2026-08-12 from the driver's own argparse `run_native_ld_panel.py:1104-1141`,
> its module docstring `:64-72`, `config/ld_regions.tsv` (header-name parse), and the
> aou-ld-pipeline SKILL — never guessed). If a DERIVED block disagrees with observed
> reality in-perimeter, STOP and report; do not improvise.

---

## 0 — NCSU side (ALREADY DONE; re-verify only)

`origin == local` was pushed before this file landed; the Workbench clone must show the
commit that contains THIS file. Nothing to do unless you committed more from NCSU.

## 1 — Workbench terminal: clone + branch [RUNBOOK item 1 + SKILL checklist]

```
git clone https://github.com/carter-clinton/coloc_analysis.git
cd coloc_analysis
git checkout m3-W2-aou-deltas
git checkout -f
git branch --show-current
```

Expect: `m3-W2-aou-deltas` (**never run from `main`** — stale unrelated history).
Then:

```
echo $WORKSPACE_BUCKET
```

Expect exactly: `gs://rw-migration-aou-rw-476cdac2`. ⚠ The variable already carries
`gs://` — **never write the scheme in front of it** (a doubled scheme empties stdout
and a piped count prints a false 0).

## 2 — bucket `.npz` count [RUNBOOK item 2]

```
gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l
```

Expect **0** pre-fire. Anything > 0 = a prior fire banked regions — reconcile before
re-firing (`force_fresh=False` semantics: the `.npz`, not the panel TSV, gates the
resume skip).

## 3 — VM state (UI only) [RUNBOOK item 3] + bfile check [DERIVED @HEAD]

In the Workbench **environment panel** (do not shell out): environment present,
**STOPPED**, `n1-standard-32`, disk intact — ⚠ **read the DISK-TYPE label**
(project rule: Reattachable persistent disk) **before any destructive env action**.
**START the environment.** Once the terminal is up:

```
ls -lh /home/jupyter/afr_cohort.bed /home/jupyter/afr_cohort.bim /home/jupyter/afr_cohort.fam
which plink || which plink1.9
df -h /home/jupyter
```

Expect: the ~354 GiB-class `.bed` plus `.bim`/`.fam` present (the fire's DIRECT
input); a plink binary on PATH (prior fires prove the env); tens of GiB free for
scratch.

## 4 — stale panel TSV (PRE-FIRE 2) [RUNBOOK item 4]

```
gsutil stat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv
```

If present:

```
gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv | head -1
```

Expected header: **9 tab-separated columns**, `n_dropped_occluded` at index **7**.
If the header does NOT match: `gsutil rm` the same URI (costs no compute; a stale
7/8-column TSV would abort the fire after ~2 regions). ⚠ "0/276 banked" does NOT
evidence the TSV's absence — prior fires appended `status=error` rows unconditionally.

## 5 — cohort-MT data layer [RUNBOOK item 5; counts DERIVED from SKILL expected shapes]

```
gsutil du -s gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt/entries/rows/parts/
```

Expect **≫ 1 GB**. ⚠ NO `/mt/` subdirectory in the path; ⚠ `_SUCCESS` is NOT evidence
of data. AND, in a Jupyter notebook on the env (Hail kernel):

```python
import hail as hl
hl.init()
mt = hl.read_matrix_table("gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt")
print(mt.count_cols(), mt.count_rows())
```

Expect non-zero both, on the order of the SKILL's recorded shape (~73,122 ×
~20,767,864). A zero or wildly-off count → **STOP; do not fire.**

## 6 — billing eyeball (UI) [RUNBOOK item 6]

Live balance in the Workbench billing panel vs the **$385–1,084** commit.

## 6b — the trsx5 byte check (GATES THE FIRE; added 2026-08-13, Seth's #1 — REWRITTEN SIZE-FIRST 2026-08-14 — ADJUDICATED-RESOLVED 2026-08-17) [RUNBOOK]

**1 — download.** In the logged-in OSF browser tab, download
https://osf.io/az52u/files/trsx5 (the **file**, not the page), then:

```
wc -c   <the downloaded file>
md5sum  <the downloaded file>
```

Report **both, verbatim**, whatever they say.

**2 — ⚠ ADJUDICATE ON THE BYTE COUNT FIRST. Expected: 9,695 bytes.** A byte
count cannot be mistranscribed into a false pass; a hash can. **ANY other size
is a STOP by itself** — no hash comparison is required and none may overrule it.
Another size means **the posted record has CHANGED** since the 2026-08-17
adjudication, and the fire is **HELD** until that is explained and recorded.
⚠ **9,758 or 9,907 observed at download time is NOW ITSELF A STOP**, not a pass —
those two were the expectations of the **SUPERSEDED** two-body card.

**3 — the hashes then confirm.**

| Observed | md5 | Meaning | Action |
|---|---|---|---|
| **9,695 B** | `c19be8b2ad7cd6a45fee1d668d8a9cf9` | the adjudicated posted body | **gate PASSES** — proceed |
| 9,695 B | anything else | same size, different content — its own anomaly | **STOP**; report verbatim |
| any other size | — | the posted record changed since adjudication | **STOP** — see step 2 |

Optional second confirm on the 9,695-B body:
`sha256 1ba83e4e633cd11c7f0896969cd6a419dada7b442365a5a0a3ea7307a342aab4`

**4 — `ADJUDICATED-RESOLVED 2026-08-17`** (per
`DEC-2026-08-17-trsx5-gate-released`). The 9,695-B body is the **verified
byte-exact plain-text rendering of the COMPLETE 9,907-B lineage** — a 6-step
transform (strip bold / italic / backticks / bullet markers, blank-line re-flow,
no trailing newline; net **−212 B**). **Replicated firsthand** from the git
object store at `3684413`, implemented from Seth's prose spec alone, **first
attempt, no fitting** — and the md5 it lands on is the one **Carter measured
himself** on his authenticated OSF download at this very gate on 2026-08-16.
⚠ `c19be8b2ad7cd6a45fee1d668d8a9cf9` is **NO LONGER "advisory, Seth-reported,
unverified"** — it is a **VERIFIED anchor**, measured independently on both
sides. **The old `{9,758, 9,907}` two-body card is SUPERSEDED.**

**5 — HISTORICAL REFERENCE, keep — neither is a live pass condition any more.**

| Historical anchor | md5 | What it is now |
|---|---|---|
| 9,758 B | `28ecdb3160833da80cfa25952f76415b` | the repo-canonical paste block — **historical reference only** |
| 9,907 B | `425d925a88ab474ec2396cbea25e665c` | the methodologist's complete lineage — retained as the **source-of-rendering** anchor for the 9,695-B body |

**Provenance of the 9,758 anchor** [DERIVED @HEAD, re-derived firsthand
2026-08-14 on the working tree **and** at `ac4c990`, both identical; the
extraction **excludes** both marker lines]:

```
F=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md
awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | wc -c
awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | md5sum
```

**6 — enforcer.** All three copies of this card are checked mechanically by
`.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh`
(V0-V7; every check was **seen red** through its own shipped sub-mode before it
was trusted). The older `260814-guk-verify.sh fire` section enforced the
**superseded** two-body card — a RED there against this card is **expected and
is not a defect**.

Rationale for the gate itself: trsx5 IS the pre-registration the fire executes;
the clauses that matter (lockstep, mandatory manifest, anomaly gate) are the ones
the fire exercises, and the question is unanswerable after output is banked. The
gate has now done its job — it held a $385-1,084 irreversible spend against a
record nobody had read, and the verification came back clean.

## 7 — sign PRE-FIRE 1b, branch (i) [RUNBOOK item 7]

Fill the **Date / Signature** lines of the decision record in
`260812-ox1-READY-TO-FIRE.md` item 7 (either side, NCSU or the clone — the constraint
is that it is signed **before STEP B**). An agent may not fill those lines.
**Re-read the branch-(ii) re-entry instruction at STEP E post-fire.**

## 8 — PRE-FIRE 3: the gated `.bim` test [pytest line RUNBOOK item 8; extraction DERIVED @HEAD]

Region-1 AFR window (from `config/ld_regions.tsv`, header-name parse):
`chr 1`, `window_start_grch38 = 10000`, `window_end_grch38 = 13506933` — the exact
bounds the driver uses (`run_native_ld_panel.py:727-728`).

```
mkdir -p data/aou
awk '($1=="1" || $1=="chr1") && $4>=10000 && $4<=13506933' /home/jupyter/afr_cohort.bim > data/aou/region1_window.bim
wc -l data/aou/region1_window.bim
pytest "tests/m3/test_occlusion_span_filter.py::test_region1_real_window_known_answer_gated" -rs -q
```

(`pip install pytest` first if absent.) Expect the row count in the ~102,421 class.
⚠ **MANUAL LINE-NUMBER COMPARISON IS FORBIDDEN** — the gated test computes both sides
in the same 0-based space and cannot false-pass on an origin error. Interpretation
[RUNBOOK]: **PASS** → PRE-FIRE 3 CLOSED, proceed. **FAIL with a uniformly ±1-shifted
set** → the oracle's base was off by one: one-line constant fix in the TEST file only
(never `occlusion_span_filter.py` — frozen), re-run. **Any other FAIL** → STOP; do not
fire; report.

## 9 — STEP A: region-1 gate [PASS criteria RUNBOOK item 9; invocation DERIVED @HEAD]

Build a one-row manifest (region 1, AFR only) and run the driver with `--fail-fast`
(its own gate flag: "Use to GATE region 1 before committing to a full 276-region
fire", `run_native_ld_panel.py:1134-1138`):

```
head -1 config/ld_regions.tsv > /tmp/region1_only.tsv
awk -F'\t' '$1=="m2_region_00001" && $7=="AFR"' config/ld_regions.tsv >> /tmp/region1_only.tsv
wc -l /tmp/region1_only.tsv
```

Expect `2` (header + one row). Then:

```
mkdir -p /home/jupyter/native_ld_scratch
python3 src/python/run_native_ld_panel.py \
  --manifest /tmp/region1_only.tsv \
  --bfile-prefix /home/jupyter/afr_cohort \
  --out-dir gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou \
  --scratch-dir /home/jupyter/native_ld_scratch \
  --mode square --ancestry AFR \
  --fail-fast
```

Rough wall expectation: the 276-region fire averages ~0.95 VM-h/region; region 1 is a
medium multi-segment window (~102k vars) — expect an hour-plus; watch the emitted JSON
line. **PASS** [RUNBOOK]: `.npz` count 0 → 1 (re-run the item-2 poll); panel
`status == "ok"`; `n_var` slightly under 102,421; `n_dropped_occluded` ≈ 5 logged; no
"not symmetric", no "Killed", no dmesg OOM. **FAIL → stop and report; do not proceed
to 276.**

**What a PASS proves (added 2026-08-13, Seth's #2 — already embedded, now explicit):**
`status == "ok"` is a MECHANISM falsification, not just a code gate — the converter
raises on ANY NaN before upload and the verifier re-scans, so a banked region 1
proves occlusion accounted for 100% of the NaN. A residual-NaN mechanism lands as
`status error` under `--fail-fast` = HARD STOP + scientific finding. After PASS,
also verify the per-region manifest at the data layer (ground truth = 5 records):

```
gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occlusion_manifest.tsv | wc -l
gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occlusion_manifest.tsv
```

Expect 6 lines (header + 5 records), all rows `m2_region_00001`.

**MECHANICAL STAGE-A GATE (AGENT-PROMPT R8; `src/python/fire_verifier.py`, landed
2026-08-18 / `quick-260818-sml`).** `git pull` first — the gate did not exist when
§1's clone instructions were written. Size the download BEFORE making it:

```
cd ~/coloc_analysis && git pull
gsutil du -h gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.npz
df -h /home/jupyter
```

Proceed only if free space is **comfortably above** the object size (it is tens of
GB). Then copy the three inputs the gate reads and run it:

```
gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.npz /home/jupyter/native_ld_scratch/
gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occlusion_manifest.tsv /home/jupyter/native_ld_scratch/
gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv /home/jupyter/native_ld_scratch/
python3 src/python/fire_verifier.py stage-a \
  --panel-tsv /home/jupyter/native_ld_scratch/m3-W2-native-plink-panel.tsv \
  --region-id m2_region_00001 \
  --manifest /home/jupyter/native_ld_scratch/m2_region_00001.occlusion_manifest.tsv \
  --npz /home/jupyter/native_ld_scratch/m2_region_00001.npz \
  --report /home/jupyter/fire_gate_stageA.json
echo "gate exit: $?"
```

Expect five checks — `stage_a_nan_falsification`, `stage_a_manifest_rows`,
`occlusion_anomaly_ceiling`, `region1_status`, `status_classification` — all PASS
and `gate exit: 0`. ⚠ **The re-read loads a ~42 GB dense float32 array and can
take many minutes. THAT IS NOT A HANG** — do not interrupt, do not restart the
kernel. **Exit 0 is required to proceed; NEVER chain past a red.** `--npz` is
REQUIRED on purpose: a falsification that did not run is not a falsification.
Then reclaim the space (the only deletion R6 authorizes):

```
rm -f /home/jupyter/native_ld_scratch/m2_region_00001.npz
df -h /home/jupyter
```

(The SH2B3 `__sub14` `estimate_s` follow-up of runbook item 9 fires LATER — once
`m2_region_00040__sub14` is banked mid-fire — it does not gate STEP B.)

## 9b — STAGED RAMP (RECOMMENDED; added 2026-08-13 on Carter's ask) [DERIVED @HEAD]

**Why staging is free:** the driver is resume-safe BY REGION — any `.npz` already in
the bucket is skipped on the next run (bucket-stat check before compute). Every
region banked in a subset run is banked forever; the final full run fills in the
rest. The ONLY staging overhead is VM idle time — **STOP the environment in the UI
between stages** (an idle `n1-standard-32` bills by the hour).

**Stage B — the de-risk batch (4 regions, deliberately diverse), right after STEP A:**

```
head -1 config/ld_regions.tsv > /tmp/stageB.tsv
awk -F'\t' '$7=="AFR" && ($1=="m2_region_00017" || $1=="m2_region_00040__sub14" || $1=="m2_region_00057" || $1=="m2_region_00071")' config/ld_regions.tsv >> /tmp/stageB.tsv
wc -l /tmp/stageB.tsv    # expect 5 (header + 4)

python3 src/python/run_native_ld_panel.py \
  --manifest /tmp/stageB.tsv \
  --bfile-prefix /home/jupyter/afr_cohort \
  --out-dir gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou \
  --scratch-dir /home/jupyter/native_ld_scratch \
  --mode square --ancestry AFR \
  --fail-fast
```

What each was picked to prove (AFR mix is 45 small / 203 medium / 28 large):
- `m2_region_00017`, `m2_region_00057` — the two SMALLEST regions (~1.05–1.18 Mb):
  fast first feedback on the whole path.
- `m2_region_00040__sub14` — **the SH2B3 / Track A anchor** and a split-parent
  `__sub` row (~75k vars): banks the one region the science gate needs, so the
  `estimate_s` identity-check (runbook item 9) can run BEFORE the big commit
  instead of mid-fire.
- `m2_region_00071` — **the largest SQUARE-FEASIBLE region (20.8 Mb window)**: the least-proven leg
  of the producer is the large class (square-mode output scales n²; disk/RAM at
  ~300k+ vars has never been measured on this VM). Running the WORST CASE now
  converts a day-9 mid-fire surprise into an early, cheap, recorded measurement
  (`wall_min` / `peak_ram_gib` land in the panel TSV either way). ⚠ If it FAILS
  (disk/RAM), that is a FINDING that bounds the deliverable for the 28-region
  large class — it does NOT block firing the other 248 regions; bring it back for
  a decision rather than papering over.

**Cost-refinement gate (after Stage B, before Stage C):** per-class average
`wall_min` from the panel TSV × the class mix (45/203/28) refines the $385–1,084
band with measured numbers. Decide the full fire on THAT estimate. ⚠ **Read it as
cost-per-BANKABLE-region, never cost-per-region-of-276** (relabelled 2026-08-14
per Seth's review): Stage B's worst case `m2_region_00071` is the largest
**square-FEASIBLE** region, so the extrapolation covers only the square-feasible
class — regions above the `--max-n-var` ceiling defer instead of computing and
are not in the denominator.

```
gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv | awk -F'\t' 'NR>1{print $1"\t"$3"\t"$4"\t"$5"\t"$7}'
```

(columns printed: region_id, n_var, wall_min, peak_ram_gib, status)

**MECHANICAL STAGE-B GATE (AGENT-PROMPT R8).** Snapshot the panel TSV and run:

```
gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv /home/jupyter/native_ld_scratch/
python3 src/python/fire_verifier.py stage-b \
  --panel-tsv /home/jupyter/native_ld_scratch/m3-W2-native-plink-panel.tsv \
  --vm-gib 120 --n-total 276 \
  --report /home/jupyter/fire_gate_stageB.json
echo "gate exit: $?"
```

Expect one `stage_b_peak_ram[<region_id>]` check per COMPUTED (`status == ok`)
row, all PASS; `status_classification` PASS; `cost_gate_denominator` PASS;
`gate exit: 0`. The bound is 15% headroom on the 120 GiB `n1-standard-32` =
**102.0 GiB**; above it, do NOT extrapolate to larger regions. A missing
`peak_ram_gib` FAILS CLOSED (unmeasurable is never ok), and ZERO computed rows
also FAILS (a check with no input must not pass vacuously). `--n-total` is a
REQUIRED argument — 276 is correct today, and a default is how a count goes
silently stale. **Exit 0 required; never chain past a red.**

⚠ **NOT WIRED — do not improvise it (A-12).** The gate also implements a
MAF-depression DIRECTION check (occluded variants should show depressed panel MAF
vs sumstats MAF; absent depression WEAKENS the occlusion attribution and is a
FINDING, not a hard stop). It stays **implemented, tested, and NOT WIRED** into
`stage-b`, and nothing in this fire changes that.

⛔ **DECIDED 2026-08-18, on Seth's recommendation: the cross-cohort
`(panel_maf, sumstats_maf)` join it would need is NOT TO BE BUILT.** It is
nobody's work item — the earlier wording calling it "Carter's planning-side work"
is retired. His courier is banked at
`.planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SETH-COURIER-d-acceptance-as-received.md`

✅ **The registered replacement is `MISS-1`**, in
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` — a
**within-panel, post-fire** missingness test (per region: `F_MISS` of the
occlusion-excluded variants against that region's own `F_MISS` distribution). If
the MAF question comes up at all, point Carter at `MISS-1` and build nothing.

**None of this blocks or changes the fire** — no new flag, no producer change, no
extra command at Stage B. If a red or a question arises here: **paste and wait —
do not improvise.**

**Stage C — the remainder:** exactly STEP B below, unchanged — everything already
banked auto-skips.

## 9c — MONITORING: what "successful" looks like, live [DERIVED @HEAD + RUNBOOK]

1. **Liveness** — the `.npz` count poll (item 2's command) CLIMBING. A count that
   stops climbing for ~a region-scale interval is the investigate signal.
2. **Quality feed** — the panel TSV is APPENDED PER REGION as the loop runs (it is
   the live per-region status feed). Status rollup — want every row `ok`:

   ```
   gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv | awk -F'\t' 'NR>1{c[$7]++} END{for(k in c) print k, c[k]}'
   ```

   Any `verify_failed` / `error: …` row: the region's artifacts stay in scratch for
   inspection; the loop continues. Investigate before Stage C; do not re-fire
   blindly.

   **MECHANICAL STAGE-C GATE (AGENT-PROMPT R8)** — run this at EVERY 2–3-day
   check-in alongside the rollup, and paste its full output:

   ```
   gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv /home/jupyter/native_ld_scratch/
   python3 src/python/fire_verifier.py stage-c \
     --panel-tsv /home/jupyter/native_ld_scratch/m3-W2-native-plink-panel.tsv \
     --report /home/jupyter/fire_gate_stageC_$(date +%Y%m%d).json
   echo "gate exit: $?"
   ```

   How to read it — this is the whole point of the gate:
   - `deferred_infeasible_square: …` / `deferred_occlusion_anomaly: …` rows
     **PASS**. They are THE GATES WORKING; never "fix" one mid-fire. (The gate
     matches these by PREFIX: the real statuses carry a detail suffix such as
     `deferred_infeasible_square: n_var=181004 > ceiling=120000`.)
   - `verify_failed` / `error: …` rows **FAIL at FINDING** — those regions banked
     NOTHING. The loop continues by design (no `--fail-fast` at Stage C); report
     them with their per-region statuses, do not re-fire blindly.
   - An **UNRECOGNIZED or EMPTY** status **FAILS at HARD_STOP** — the producer
     emitted something the gate does not know, or the panel TSV is corrupt. Stop
     and report immediately.

   Exit 0 = nothing to report beyond the counts. **Never chain past a red.**
3. **The log** — `tail -20 /home/jupyter/native_ld_fire.log` and
   `grep -cE "VERIFY-FAILED|^ERROR" /home/jupyter/native_ld_fire.log` (want 0).
4. **Built-in content gate (the reason bucket presence ≈ success):** every `.npz`
   is content-verified BEFORE upload (`content_verify_npz`: symmetry, unit
   diagonal, NaN scan) and uploads only inside `if ok:` — a bucket `.npz` is
   verified by construction. The per-region occlusion manifest + `.afreq` +
   excludelist ride the same gate.
5. **Optional in-perimeter spot-check ($0)** — after Stage B, on the VM:

   ```
   gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00017.npz /tmp/ && python3 -c "
   import numpy as np
   z = np.load('/tmp/m2_region_00017.npz', allow_pickle=False)
   print(sorted(z.files)); print(z['ld'].shape, z['ld'].dtype)"
   ```

   Expect the documented keys (incl. the triangle flag) and an n_var × n_var
   float32 `ld`.

## ✅ STAGE C HOLD LIFTED (2026-08-13)

✅ Lifted 2026-08-13, commit d9fbc63: both producer gates are
wired in run_native_ld_panel.py — the pre-registered clause-(d) anomaly gate
(0.0005 x n_var, defer-not-exclude) and the --max-n-var feasibility ceiling
(default 120000 = the consumer's m3_convert_max_n_var). `git pull` on the VM
before Stage C. In the panel TSV, `deferred_infeasible_square` and
`deferred_occlusion_anomaly` rows are THE GATES WORKING — expected for ~29+
regions above the ceiling; the bankable target is 276 MINUS deferrals, and no
deferral count is a pre-committed expectation (the count emerges at fire time).
The STEP-10 monitoring rollup already keys by status: report ok /
deferred_infeasible_square / deferred_occlusion_anomaly / error counts
SEPARATELY. The fire invocation is unchanged (no new flag needed; the default
ceiling is the gate) and Stage C still runs WITHOUT --fail-fast — with it,
the first deferral would halt the loop.

## 10 — STEP B: THE FIRE [caveats RUNBOOK item 10; invocation DERIVED @HEAD]

```
nohup timeout 312h python3 src/python/run_native_ld_panel.py \
  --manifest config/ld_regions.tsv \
  --bfile-prefix /home/jupyter/afr_cohort \
  --out-dir gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou \
  --scratch-dir /home/jupyter/native_ld_scratch \
  --mode square --ancestry AFR \
  > /home/jupyter/native_ld_fire.log 2>&1 &
echo "fire PID: $!"
```

No `--fail-fast` here — the full loop is resume-safe continue by design (a partial
bank is a real, reportable outcome). Region 1 is already banked and will be SKIPPED by
the bucket-stat resume check. `nohup` survives browser disconnects (the SKILL's
invariant 3: a clean disconnect does not kill the server-side job; do **NOT** restart
the kernel). **Teardown is UI-only**; `timeout 312h` (13-day wall-cap) is the
backstop.

**Liveness = the `.npz` listing climbing toward 276 — NOT the kernel light, NOT
`_SUCCESS`, NOT the log.** Check in every **2–3 days**:

```
gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l
```

⚠ Never prefix `$WORKSPACE_BUCKET` with the scheme; on any surprising 0 → literal
form + read stderr first. ⚠ **276 IS NOT A PASS BAR** — `verify_failed` regions never
upload, per-region errors continue the loop; a count that **stops climbing** is the
signal to investigate, not a number to wait out.

**Mid-fire checkpoint:** when `m2_region_00040__sub14.npz` appears, run the SH2B3
`estimate_s` check of runbook item 9 (if `ld_matrix` reads `identity`, report with the
observed `ld_overlap` / `ld_overlap_fraction`; the three remedies are scientific
calls).

## After — STEP C/D/E/F/G

Per runbook item 11 (egress sizing → per-group egress + audit rows + SHA-256
sub-manifests → catalog rule under the SIGNED 1b branch (re-read its (ii) re-entry) →
the Check-2 OSF amendment-update (agent drafts, Carter posts) → the end-to-end
read-path proof). Full text: review §5.
