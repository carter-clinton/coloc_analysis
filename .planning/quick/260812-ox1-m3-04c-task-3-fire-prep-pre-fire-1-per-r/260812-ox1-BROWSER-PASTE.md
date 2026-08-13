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
gsutil du -s gs://rw-migration-aou-rw-476cdac2/ld/mt_AFR_qc.mt/entries/rows/parts/
```

Expect **≫ 1 GB**. ⚠ NO `/mt/` subdirectory in the path; ⚠ `_SUCCESS` is NOT evidence
of data. AND, in a Jupyter notebook on the env (Hail kernel):

```python
import hail as hl
hl.init()
mt = hl.read_matrix_table("gs://rw-migration-aou-rw-476cdac2/ld/mt_AFR_qc.mt")
print(mt.count_cols(), mt.count_rows())
```

Expect non-zero both, on the order of the SKILL's recorded shape (~73,122 ×
~20,767,864). A zero or wildly-off count → **STOP; do not fire.**

## 6 — billing eyeball (UI) [RUNBOOK item 6]

Live balance in the Workbench billing panel vs the **$385–1,084** commit.

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

(The SH2B3 `__sub14` `estimate_s` follow-up of runbook item 9 fires LATER — once
`m2_region_00040__sub14` is banked mid-fire — it does not gate STEP B.)

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
