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
which plink1.9 && plink1.9 --version
df -h /home/jupyter
```

Expect: the ~354 GiB-class `.bed` plus `.bim`/`.fam` present (the fire's DIRECT
input); **`plink1.9` on PATH printing `PLINK v1.90b7.2 64-bit (11 Dec 2023)`** — the
producer's argv names the literal `plink1.9` and the pilot/fire brief pin that build
(2026-08-24: the VM image ships only `plink`; Stage A stopped on Errno 2 — the old
`which plink || which plink1.9` passed on the wrong binary); tens of GiB free for
scratch. If `plink1.9` is absent, install the pinned build into `~/bin` and export
`PATH="$HOME/bin:$PATH"` in the SAME shell that runs STEP 8 (recipe in the
AGENT-PROMPT STEP 3); never shim a PLINK 2.x binary.

## 4 — stale panel TSV (PRE-FIRE 2) [RUNBOOK item 4] — bucket copy AND the local scratch mirror

⚠ Added 2026-08-24: also check `/home/jupyter/native_ld_scratch/m3-W2-native-plink-panel.tsv`
(`head -1`, `wc -l`). The producer seeds its mirror from that local file when the bucket
copy is absent and fail-closes on a stale header — Stage A stopped on a June-era 7-column
leftover there. A stale local mirror is ROTATED (`mv … .STALE.<UTC>`), never deleted.

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
pytest "tests/m3/test_occlusion_span_filter.py::test_region1_real_window_known_answer_gated" \
       "tests/m3/test_occlusion_span_filter.py::test_region1_real_window_substrate_totals_MEASURED_NOT_DERIVED" \
       "tests/m3/test_occlusion_span_filter.py::test_containment_assertions_discriminate_a_wrong_answer" \
       -rs -q
```

(`pip install pytest` first if absent.) Expect the row count **102,421**.

**Two layers, deliberately separate (re-derived 2026-08-21):**

* **LAYER 1 — DERIVED** (`..._known_answer_gated`): asserts **CONTAINMENT**, not
  equality. The settled-5 occluded **row indices** and the 7 settled REF spans must be
  **PRESENT**. The real window legitimately carries far more of both — **231 occluded
  rows** over **7,951 multi-base-REF rows**, max span **170 bp**, MEASURED 2026-08-19.
  The old `==` was false about the window while true only about the June-2026 NaN-pair
  forensics.
* **LAYER 2 — MEASURED** (`..._substrate_totals_MEASURED_NOT_DERIVED`): pins
  `n_rows 102421 / n_deletion_rows 7951 / n_occluded_rows 231 / max_span 170 /
  n_sites 96708 / occ_sites 196`.
* the third selector is the unconditional control proving containment can still fail.

⚠ **MANUAL LINE-NUMBER COMPARISON IS FORBIDDEN** — the gated test computes both sides
in the same 0-based space and cannot false-pass on an origin error. Interpretation
[RUNBOOK]: **PASS** → PRE-FIRE 3 CLOSED, proceed. **LAYER 1 FAIL with a uniformly
±1-shifted set** → the oracle's base was off by one: one-line constant fix in the TEST
file only (never `occlusion_span_filter.py` — frozen), re-run. **LAYER 2 FAIL** → the
SUBSTRATE moved (a CDR refresh does this): **RE-MEASURE AND RECORD** with fresh
provenance and re-check every consumer — never edit the number to green. **Any other
FAIL** → STOP; do not fire; report.

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
`status == "ok"`; `n_var` slightly under 102,421; **`n_dropped_occluded == 231`**
(MEASURED 2026-08-19/20 — 231 occluded ROWS at 196 sites, of 96,708 sites / 102,421
rows; source `.planning/debug/260820-site-basis-sweep-results-as-received.md`); no
"not symmetric", no "Killed", no dmesg OOM. **FAIL → stop and report; do not proceed
to 276.**

**THE ARBITER RULE.** If the observed count differs from 231, the per-region sidecar
`m2_region_00001.occlusion_gate.json` is the **arbiter** — it is the shipped gate's own
measurement — and the run **STOPS for re-measurement**. Never edit-to-green, never
"close enough", never split the difference.

**What a PASS proves (added 2026-08-13, Seth's #2 — already embedded, now explicit):**
`status == "ok"` is a MECHANISM falsification, not just a code gate — the converter
raises on ANY NaN before upload and the verifier re-scans, so a banked region 1
proves occlusion accounted for 100% of the NaN. A residual-NaN mechanism lands as
`status error` under `--fail-fast` = HARD STOP + scientific finding. After PASS,
also verify the per-region manifest at the data layer (MEASURED = 231 records):

```
gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occlusion_manifest.tsv | wc -l
gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occlusion_manifest.tsv | head -20
```

Expect **232 lines (header + 231 records)**, all rows `m2_region_00001`.

**THE GATE SIDECAR — read it, it is the arbiter:**

```
gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occlusion_gate.json
```

EXPECT: `occ_rows 231`, `occ_sites 196`, `n_sites 96708`, `site_fraction ≈ 0.2027%`
(the JSON carries the BARE FRACTION, ≈ 0.002027), `inflation ≈ 1.18x`, `fired []`,
`verdict "ok"`. The manifest line count, the panel row's `n_dropped_occluded` and the
sidecar's `occ_rows` are three records of ONE drop set — any disagreement **STOPS the
run for re-measurement**.

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
gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occlusion_gate.json /home/jupyter/native_ld_scratch/
gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occluded.excludelist /home/jupyter/native_ld_scratch/
gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv /home/jupyter/native_ld_scratch/
python3 src/python/fire_verifier.py stage-a \
  --panel-tsv /home/jupyter/native_ld_scratch/m3-W2-native-plink-panel.tsv \
  --region-id m2_region_00001 \
  --manifest /home/jupyter/native_ld_scratch/m2_region_00001.occlusion_manifest.tsv \
  --npz /home/jupyter/native_ld_scratch/m2_region_00001.npz \
  --gate-json /home/jupyter/native_ld_scratch/m2_region_00001.occlusion_gate.json \
  --excludelist /home/jupyter/native_ld_scratch/m2_region_00001.occluded.excludelist \
  --report /home/jupyter/fire_gate_stageA.json
echo "gate exit: $?"
```

Expect **six** checks — `stage_a_nan_falsification`, `expected_records_derivation`,
`stage_a_manifest_rows`, `occlusion_gate`, `region1_status`, `status_classification` —
all PASS and `gate exit: 0`. **Do NOT pass `--expected-records`:** the gate DERIVES the
expected manifest record count from the excludelist's line count and cross-checks it
against the sidecar's `occ_rows`. The flag survives only as an override, is logged as
one, and has no use here. ⚠ **The re-read loads a ~42 GB dense float32 array and can
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
  converts a day-9 mid-fire surprise into an early, cheap, recorded measurement.
  ⚠ **CORRECTED 2026-09-16 (`quick-260916-vqr`):** the retired parenthetical here
  claimed `wall_min` / `peak_ram_gib` land in the panel TSV **regardless of
  outcome**. That is FALSE. If **plink itself** fails, `_run_plink` **RAISES**
  before `process_region` ever assigns `result["wall_min"]` /
  `result["peak_ram_gib"]`, so **BOTH stay `None`** and the row records
  `error: …`. What that costs is specific: the worst-case RAM/wall figure that is
  the entire reason `m2_region_00071` is in Stage B is exactly the thing that does
  not survive its failure. (Both symbols cited BY NAME — `_run_plink`,
  `process_region` — never by line number, which drifts.)
  ⚠ If it FAILS
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

⚠ **HOW TO READ `peak_ram_gib` — IT IS PLINK-ONLY** (added 2026-09-16,
`quick-260916-vqr`). This changes what a PASS here licenses:

- Since the RAM-1 launcher landed (`9a3eb97`), `peak_ram_gib` is **plink's OWN
  peak RSS**, read by a small isolated launcher via `os.wait4` — **not** the
  driver's memory. The launcher's own bias is ~11 MiB (measured 0.0107–0.0110 GiB
  for a bare `true` on python 3.11, NCSU 2026-09-16);
  `tests/m3/test_run_plink_peak_rss.py` bounds that bias under **24 MiB**
  (`_BIAS_CEIL_MIB`).
- **The driver's own largest load is NOT in that column.** After plink exits,
  `plink_ld_to_npz.read_square_bin` `np.fromfile`s the whole `.ld.bin` into ONE
  dense `float32` array inside the driver process = **4 · n_var² bytes**: at
  n_var 102,421 that is **39.08 GiB**, and at the `--max-n-var` ceiling of 120,000
  it is **53.64 GiB**. The NaN / unit-diagonal / symmetry scans are deliberately
  BLOCKED (`plink_ld_to_npz._has_any_nan_blocked`, block=1024) so they add about
  `block · n_var` bytes rather than another n_var² — but `content_verify_npz`
  then **re-loads** the banked array afterwards. **State 4 · n_var² as a FLOOR:**
  the driver's true peak has not been measured anywhere.
- Therefore `fire_verifier.check_peak_ram` (15% headroom on 120 GiB = **102.0
  GiB**) now bounds **plink only**. plink reserves roughly half of detected RAM by
  default, so a PASS there is **not** headroom evidence for the driver. **Add the
  driver term separately** when reading this gate, sizing the VM, or computing
  `COST-1`.
- **The four rows already in the bucket panel TSV are PRE-FIX and must be
  quarantined:** `m2_region_00001 30.6591`, `m2_region_00017 2.9689`,
  `m2_region_00040__sub14 26.5745`, `m2_region_00057 26.5745`. They were written
  **before** `9a3eb97`, so they are **not** plink-only measurements. The panel TSV
  carries no code-version column and nothing mechanically separates them — **do
  not mix them with post-fix values.** `COST-1` uses post-fix rows only; if a
  class has no post-fix row, say so rather than substituting a pre-fix one.

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

   **STAGE-C RAISE POSTURE — read this before you read the gate output.**
   A `raised_nan: square LD carries NaN …` row is **the pre-registered contract
   firing as committed — not a defect, and not a deviation.** The region banked
   NOTHING; the loop continues by design. Four rules:

   1. **CONTINUE on a KNOWN-CLASS raise.** The known class is the
      `m2_region_00057` shape (measured 2026-08-24): a *confined symmetric pair*
      — 2 NaN cells out of n_var², both rows `nan_count 1`, both diagonals
      `1.0`, `PATTERN = confined pair? True`, `whole-row (zero-variance)? False`
      — i.e. one pairwise-undefined correlation at a deletion-span boundary, not
      a zero-variance variant.
   2. **STOP on an UNCLASSIFIED raise**, and report it. There is **no
      classification mechanism in the pipeline today** (the per-region pre-check
      is deferred until COST-1 measures a per-region wall time), so this is your
      judgement call against the reported region id and `n_var` — not a lookup.
   3. **Re-diagnosis CLASSIFIES. It never changes the inputs or the criterion.**
      No re-running a region with different data, no touching the occlusion
      criterion — that is pre-registered and moving it needs a new posted
      amendment FIRST.
   4. **A stop that is not resumed TRUNCATES THE CLOSEOUT DENOMINATOR.** Every
      region after the stop is unbanked and unmeasured, and that has to be
      disclosed. Stopping is cheap; stopping and not resuming is not.

   **RESUME, exactly:** resume skips a region only if its `.npz` is **ALREADY IN
   THE BUCKET**, so **every region that banked nothing — `error:`,
   `verify_failed` and BOTH `deferred_*` classes — recomputes on resume.**
   (Coordinate-only gate evidence in the bucket does **not** count: the skip keys
   on the `.npz` alone.)

   ⚠ **This is the ONE documented exception to "Any red = STOP".** An
   acknowledged, known-class `raised_nan:` row that the gate re-reports is not a
   new stop. Everything else still is.

   ```
   gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv /home/jupyter/native_ld_scratch/
   python3 src/python/fire_verifier.py stage-c \
     --panel-tsv /home/jupyter/native_ld_scratch/m3-W2-native-plink-panel.tsv \
     --report /home/jupyter/fire_gate_stageC_$(date +%Y%m%d).json \
     --prev-report /home/jupyter/fire_gate_stageC_<THE PREVIOUS CHECK-IN'S DATE>.json
   echo "gate exit: $?"
   ```

   ⚠ `--prev-report` names the **previous** check-in's file and must **never** be
   the same path as `--report` — the report is written AFTER the checks, so that
   would read the acknowledged set and then destroy it. That case is refused
   before any check runs, with nothing written. Omit `--prev-report` at the FIRST
   check-in only. **The check-in is stateful:** exit 1 means something entered a
   stop-worthy state SINCE that report; an already-acknowledged raise or failure
   is still counted and still listed, just not a new stop. A row that DISAPPEARED
   is a HARD_STOP (the TSV is append-only — if you rotated it deliberately, run
   once without `--prev-report` to re-mint a baseline and say so). A missing or
   pre-change `--prev-report` FAILS CLOSED.

   ⚠ **Before the first region completes, both the `gsutil cp` and this gate will
   FAIL — that is the gate failing CLOSED, not a fire defect.** No panel TSV in
   the bucket yet → the cp errors and the gate reports `stage-c_driver …
   FileNotFoundError … -> FAIL CLOSED`; a header-only TSV → the
   `stage_c_zero_data_rows` HARD_STOP, which names its five routes in. The first
   meaningful check-in is after the first `.npz` appears. Report it either way; do
   not re-fire, and do not hand-create a panel TSV to make the gate green.

   How to read it — this is the whole point of the gate:
   - `deferred_infeasible_square: …` / `deferred_occlusion_anomaly: …` rows
     **PASS**. They are THE GATES WORKING; never "fix" one mid-fire. (The gate
     matches these by PREFIX: the real statuses carry a detail suffix such as
     `deferred_infeasible_square: n_var=181004 > ceiling=120000`.)
   - `verify_failed` / `error: …` rows **FAIL at FINDING** — those regions banked
     NOTHING. The loop continues by design (no `--fail-fast` at Stage C); report
     them with their per-region statuses, do not re-fire blindly.
   - `raised_nan: square LD carries NaN …` rows are **the pre-registered raw-panel
     NaN contract firing as committed** — not a defect and not a deviation (added
     2026-09-18, `quick-260918-qz5`). The region banked NOTHING and the loop
     continues by design; its coordinate-only gate evidence (`.occlusion_gate.json`,
     plus `.occluded.excludelist` / `.occlusion_manifest.tsv` when they exist) **is**
     in the bucket so the closeout distributions fold it in, and its `.npz` is not
     and never will be. The gate reports it in its OWN check
     (`raised_nan_contract_fired`, a FINDING with the count and region list),
     never as a deferral and never as an operational failure — so it can no longer
     be confused with a scratch-full or a gsutil failure, which is what `error:`
     now means on its own. **THE CONDITIONAL STOP:** continue on a known-class
     raise; **STOP and report** on an UNCLASSIFIED one (see the four rules above).
   - An **UNRECOGNIZED or EMPTY** status **FAILS at HARD_STOP** — the producer
     emitted something the gate does not know, or the panel TSV is corrupt. Stop
     and report immediately. ⚠ An unknown status is **never acknowledgeable**: it
     HARD_STOPs even if it appears in the `--prev-report`.

   Exit 0 = nothing to report beyond the counts — ⚠ **amended 2026-09-18**, because
   with `--prev-report` exit 0 can mean "one ACKNOWLEDGED raise, still counted":
   it means nothing **NEW** since the last check-in. The counts still carry every
   acknowledged raise and must still be pasted in full. **Never chain past a red**
   — with the ONE documented exception above.
3. **The log** — `tail -20 /home/jupyter/native_ld_fire.log` and
   `grep -cE "VERIFY-FAILED|^ERROR|^RAISED-NAN" /home/jupyter/native_ld_fire.log`
   (want 0). ⚠ `|^RAISED-NAN` was added 2026-09-18 (`quick-260918-qz5`): the
   producer logs a raw-panel NaN raise as `RAISED-NAN <region_id>: …`, so without
   it a raise was INVISIBLE to this monitor. A non-zero `RAISED-NAN` count is the
   contract firing, **not** a defect — read it with the conditional stop above.
   `VERIFY-FAILED` and `^ERROR` still want 0.
4. **Built-in content gate (the reason bucket `.npz` presence ≈ success):** every
   `.npz` is content-verified BEFORE upload (`content_verify_npz`: symmetry, unit
   diagonal, NaN scan) and uploads only inside `if ok:` — a bucket `.npz` is
   verified by construction. ⚠ **CORRECTED 2026-09-18 (`quick-260918-qz5`): the
   per-region occlusion manifest, the `.afreq`, the excludelist and the gate
   sidecar NO LONGER ride that gate.** Those four now cross on EVERY square
   outcome — `ok`, `verify_failed`, `error:` and `raised_nan:` alike — because
   `mk7ze` P248-250 commits that every region's own occlusion count AND
   occluded-site inflation fold into the closeout distributions, and previously a
   region that did not reach `ok` had its gate evidence die in VM scratch. **Only
   the `.npz` rides the `if ok:` gate.** So the presence of those four does NOT
   imply a banked region — only `.npz` presence does, which is why liveness is
   the **`.npz`** count climbing and never the object count. Safe by construction:
   the resume skip keys on the `.npz` alone at the `_MIN_REGION_NPZ_BYTES` floor,
   so a stray coordinate artifact cannot fake a banked region.
5. **Optional in-perimeter spot-check ($0)** — after Stage B, on the VM:

   ```
   gsutil cp gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00017.npz /tmp/ && python3 -c "
   import numpy as np
   z = np.load('/tmp/m2_region_00017.npz', allow_pickle=False)
   print(sorted(z.files)); print(z['ld'].shape, z['ld'].dtype)"
   ```

   Expect the documented keys (incl. the triangle flag) and an n_var × n_var
   float32 `ld`.
6. **Operational notes for the RAM-1 launcher** (added 2026-09-16,
   `quick-260916-vqr`). Since `9a3eb97` plink is spawned by a small isolated
   launcher process; three observable consequences, each with its scope:

   - **A SIGKILL to the launcher alone — or an OOM kill of it — ORPHANS plink.**
     The region records `error: …` and the loop moves on, so the orphaned plink
     keeps running while the **next** region's plink starts: two concurrent
     plinks, and the scratch of both. Report it with the panel TSV row rather than
     improvising. The reassuring half, so you do not over-react: **no region is
     recorded `ok` by mistake and no region runs twice** — there is no retry path.
   - **`pgrep -f plink1.9` / `pkill -f plink1.9` now ALSO match the launcher**
     (its argv carries plink's argv, and its lower PID lists first, so a naive
     "first hit" reads the wrong process). Use **`pgrep -x plink1.9`** — it
     matches the plink process only. ⚠ And the trap that cost a false result
     during the work that wrote this note: an `-f` pattern can also match the
     probing shell itself.
   - **The launcher runs python `-I -S`, which can add `LC_CTYPE=C.UTF-8` to
     plink's environment** — but ONLY in the narrow case `LANG=C` **and**
     `PYTHONCOERCECLOCALE=0` together: isolated mode implies `-E`, so the opt-out
     is ignored (measured on python 3.11.15, 2026-09-16). With
     `PYTHONCOERCECLOCALE` unset the driver already coerced the locale before
     RAM-1 and plink sees the value it always did. A note for reading plink's
     behaviour, not an action.
   - The launcher's own failure messages do **not** name the launcher — which is
     exactly why §9d check 1 lists the four signatures by exception type.

## ✅ STAGE C HOLD LIFTED (2026-08-13)

✅ Lifted 2026-08-13, commit d9fbc63: both producer gates are
wired in run_native_ld_panel.py — the pre-registered clause-(d) occlusion gate
(RECALIBRATED 2026-08-22 to the POSTED TWO-condition rule, defer-not-exclude:
DEFER when EITHER the occluded-SITE fraction exceeds 0.5056% OR the occluded-site
row/site inflation exceeds 3.42x, STRICT `>` on both — OSF file mk7ze,
https://osf.io/mk7ze) and the --max-n-var feasibility ceiling
(default 120000 = the consumer's m3_convert_max_n_var). `git pull` on the VM
before Stage C. Region 1 sits at 0.2027% and 1.18x — under BOTH — so a deferral
there would itself be the finding. In the panel TSV, `deferred_infeasible_square` and
`deferred_occlusion_anomaly` rows are THE GATES WORKING — expected for ~29+
regions above the ceiling; the bankable target is 276 MINUS deferrals, and no
deferral count is a pre-committed expectation (the count emerges at fire time).
The STEP-10 monitoring rollup already keys by status: report ok /
deferred_infeasible_square / deferred_occlusion_anomaly / error counts
SEPARATELY. The fire invocation is unchanged (no new flag needed; the default
ceiling is the gate) and Stage C still runs WITHOUT --fail-fast — with it,
the first deferral would halt the loop.

## 9d — FIRE-SHELL PRECONDITIONS ($0, under a minute; added 2026-09-16, `quick-260916-vqr`)

**Run all four in the SAME SHELL THAT WILL FIRE** — the shell in which §1/§3's
`export PATH="$HOME/bin:$PATH"` was done. A new tab is a *different* shell and
proves nothing about the one that matters.

**Why this exists, in two lines.**

- **The launcher has never run for real.** Stage A and Stage B regions auto-skip
  once banked, so Stage C — 11 days, unattended, no `--fail-fast` — is the first
  real run of `_run_plink` for almost every region.
- **Errors are sticky.** Panel rows are FIRST-ROW-WINS: `append_panel_row` dedups
  by `region_id` and returns on a region already present —
  `if str(out_row["region_id"]) in set(existing["region_id"].astype(str)): return`
  (cited BY SYMBOL; the line number drifts). An environment defect that errors
  every region writes error rows a re-fire will **not** replace.

**1) THE SMOKE — the PRIMARY check; it exercises the whole shipped seam.**

```
python3 -c 'import sys;sys.path.insert(0,"src/python");import run_native_ld_panel as r;print(r._run_plink(["plink1.9","--version"]))'
```

**EXPECT TWO LINES, NOT ONE.** plink inherits fd 1, so its own version banner
arrives FIRST, then the tuple:

```
<plink's version banner line>
(<wall_min>, <peak_ram_gib>)
```

**The banner is expected** — neither noise nor a failure. `wall_min` is a small
fraction of a minute (measured **33–56 ms** at NCSU); `peak_ram_gib` is a **small
non-zero** number on the order of the launcher's own floor (measured
**0.0107–0.0110 GiB ≈ 11 MiB** on python 3.11;
`tests/m3/test_run_plink_peak_rss.py` bounds a bare `true` **under 24 MiB**,
`_BIAS_CEIL_MIB`). The check spawns plink for **tens of milliseconds** and
computes nothing — it is **$0**.

⚠ Do **not** expect a specific banner string, and do **not** assume exit 0: the
VM's pinned build prints its own version line and **that build's `--version` exit
status is UNMEASURED**. If it returns non-zero, `CalledProcessError` below is the
expected outcome and the banner is the evidence — report it, do not improvise.

**Anything else is a STOP under R3.** The four signatures you will actually see:

- `FileNotFoundError: [Errno 2] No such file or directory: 'plink1.9'` → **PATH**:
  `plink1.9` is not on *this* shell's PATH. Go back to the pinned install and
  re-export PATH **in this shell**. (The 2026-08-24 Stage A stop, unchanged.)
- `subprocess.SubprocessError: plink peak-RSS launcher exited 0 without a valid
  report; refusing to fabricate wall_min/peak_ram_gib for [...]` → SIGCHLD is
  ignored, or `sys.executable` is odd. Go to check **3**.
- `AttributeError` / `ModuleNotFoundError` on import → interpreter or environment.
  Go to check **2**.
- `subprocess.CalledProcessError: Command '[...]' returned non-zero exit status N`
  → **plink ran and returned non-zero.** Read its banner and report it.

**2) THE INTERPRETER.**

```
python3 -V; which python3
```

**Record both** — neither has ever appeared in an as-received record for this VM.
**Python ≥ 3.9 is REQUIRED:** the launcher binds `os.waitstatus_to_exitcode`
**before** the spawn (`run_native_ld_panel.py`, "bound BEFORE the spawn"),
precisely so an interpreter without it fails *before* plink runs rather than after
hours of compute. Below 3.9 → **STOP**.

**3) SIGCHLD MUST NOT BE IGNORED.**

```
V=$(grep '^SigIgn' /proc/self/status | awk '{print $2}'); if [ $(( 0x$V & 0x10000 )) -eq 0 ]; then echo "SigIgn=$V  SIGCHLD-OK"; else echo "SigIgn=$V  STOP: SIGCHLD is SIG_IGN"; fi
```

EXPECT `SIGCHLD-OK`. ⛔ **The pass condition is the BIT, never the whole mask.**
SIGCHLD is signal 17, so its mask bit is `1 << 16 = 0x10000`. Measured
2026-09-16: a **non-interactive** shell reads `0000000000000000`, while an
**interactive** shell — which is what this VM terminal is — reads
`0000000000380000` (bits 19/20/21 = `SIGTSTP`/`SIGTTIN`/`SIGTTOU`, exactly what
any interactive shell ignores). **Both are GREEN.** Publishing a whole-mask
expectation would **false-STOP a healthy fire**. The RED readings in the same
measurement were `0000000000010000` and `0000000000390000` — each differing from
its green partner in the `0x10000` bit alone, which is why only that bit decides.

*Why it matters:* with SIGCHLD inherited as `SIG_IGN`, `os.wait4` raises
`ChildProcessError` and **every** region raises — and the pre-RAM-1
`subprocess.run` silently returned 0, so nothing else in the pipeline notices.

*Scope, stated honestly:* on GNU coreutils 8.32 `timeout` **resets** SIGCHLD to
`SIG_DFL` before exec, so the §10 fire command is additionally shielded (measured
2026-09-16: bare `python3` → bit set; `nohup python3` → bit set; `timeout …
python3` in either command order → bit **clear**). But Stage A (§9), Stage B
(§9b) and **every bare `python3 src/python/…` invocation, including the three
`fire_verifier.py` gate runs, are NOT shielded** — and this VM's coreutils version
is unmeasured. The shell-level check above is the version-independent cover.

**4) THE SIGHUP PROPERTY CHECK — does the fire actually survive a browser
disconnect on THIS VM's own coreutils?** (~10 s, $0.) It is here because the
command form was decided on GNU coreutils 8.32 at NCSU and this VM's version is
**unmeasured**.

```
REPO=$PWD   # ⚠ remember where the fire runs from; check 4 ends by returning here
cd /tmp && cat > hupchild.py <<'PYEOF'
import os, sys, time
open(sys.argv[1], "w").write(str(os.getpid()))
time.sleep(90)
PYEOF
alive(){ s=$(ps -o stat= -p "$1" 2>/dev/null | tr -d ' '); if [ -z "$s" ] || [ "${s#Z}" != "$s" ]; then echo DEAD; else echo ALIVE; fi; }
set -m
rm -f /tmp/pidA /tmp/pidB
nohup timeout 40 python3 /tmp/hupchild.py /tmp/pidA > /tmp/hupA.log 2>&1 &
LA=$!; sleep 2; CA=$(cat /tmp/pidA); kill -HUP $LA; sleep 2
echo "formA  launcher=$(alive $LA) child=$(alive $CA)"
kill -9 $CA $LA 2>/dev/null
timeout 40 nohup python3 /tmp/hupchild.py /tmp/pidB > /tmp/hupB.log 2>&1 &
LB=$!; sleep 2; CB=$(cat /tmp/pidB); kill -HUP $LB; sleep 2
echo "formB  launcher=$(alive $LB) child=$(alive $CB)"
kill -9 $CB $LB 2>/dev/null
timeout 3 nohup python3 /tmp/hupchild.py /tmp/pidC > /dev/null 2>&1; echo "expiry rc=$?"
cd "$REPO" && pwd   # ⚠ MANDATORY: check 4 cd'd to /tmp; the fire uses RELATIVE paths
```

EXPECT these three propositions, in this order, followed by the repo path:

```
formA  launcher=DEAD child=DEAD
formB  launcher=ALIVE child=ALIVE
expiry rc=124
/home/jupyter/coloc_analysis          <- whatever $REPO was; the cd-back, NOT optional
```

⚠ bash may interleave its own job notices (`… Hangup …`, `… Killed …`) around those
lines — that is the shell reporting the probe's own children and is EXPECTED; judge the
three propositions and the final path, not the line count. ⛔ If the last line is `/tmp`
or the `cd` is missing, STOP: the fire command uses RELATIVE paths (`src/python/…`,
`config/ld_regions.tsv`) and would fail from the wrong directory while `echo "fire PID: $!"`
still prints a PID — it reads as launched and is not.

**Read it as a property, not as a hope.** form A's **death** is the NEGATIVE
CONTROL that makes form B's survival mean anything. ⛔ **If both forms survive, or
both die, or the expiry line is not 124, the property did not reproduce on this VM
→ STOP under R3 and report. DO NOT FIRE.**

The `expiry rc=124` line is the **backstop control**: form B does not trade the
312h wall-cap away for survival. Measured 2026-09-16 at NCSU — a form-B job HUP'd
at t=2 s under a 6 s cap was still ALIVE at t+1 s and **DEAD at t+9 s**, so the
cap still fired after the SIGHUP; the same run showed the child surviving a SIGHUP
sent to the pid **and** to its whole process group.

⚠ **Identify the child by PIDFILE, as above. Never `pgrep -f <pattern>` here:** an
`-f` pattern matches the probing shell's own command line and self-matches, which
already produced one false result during the work that wrote this step. The
`kill -9` lines leave nothing running; the check spawns two sleeps and computes
nothing.

## 10 — STEP B: THE FIRE [caveats RUNBOOK item 10; invocation DERIVED @HEAD]

```
timeout 312h nohup python3 src/python/run_native_ld_panel.py \
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
the bucket-stat resume check. §9d must have been run in THIS shell, all four checks
green.

⚠ **COMMAND FORM CORRECTED 2026-09-16 (`quick-260916-vqr`).** The retired wording
here read "`nohup` survives browser disconnects (the SKILL's invariant 3: a clean
disconnect does not kill the server-side job)", and the committed command was form
A, `nohup timeout 312h python3 …`. **That was false**, and it is retired rather
than deleted so the correction stays legible. In form A, `nohup`'s ignore-SIGHUP
applies to **`timeout`**, which **forwards** the signal to its child — MEASURED
2026-09-16 on GNU coreutils 8.32: **the child DIED**. The form now above (form B,
`nohup` INSIDE `timeout`) survived a SIGHUP sent to the pid **and** to the whole
process group, child alive in both cases. The SKILL's invariant 3 is about the
**Dataproc master-side job** and is not a warrant for this VM fire (it now says so
itself).

*What did not change:* `$!` still names the `timeout` process under both forms
(`ps -o comm= -p $!` printed `timeout`), so `echo "fire PID: $!"` keeps its meaning
and teardown guidance is unchanged. **Do NOT restart the kernel.** **Teardown is
UI-only**; `timeout 312h` (13-day wall-cap) is still the backstop and **remains
armed after a SIGHUP** (measured). **Prove the property on THIS VM first — §9d
check 4.**

⚠ The fire log's FIRST line will be `nohup: ignoring input` whenever this terminal
has job control — measured under **both** command forms, so it is
form-independent. It is not an error, it does **not** match the
`grep -cE "VERIFY-FAILED|^ERROR|^RAISED-NAN"` monitor, and no `nohup.out` appears
in the cwd because the shell's `> …fire.log 2>&1` already owns stdout.
⚠ That monitor gained `|^RAISED-NAN` on 2026-09-18 (`quick-260918-qz5`) — kept in
step with the operator's actual command in §3 above, because leaving a stale copy
of a monitor in a descriptive note is how the next reader concludes the command
was never changed.

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
