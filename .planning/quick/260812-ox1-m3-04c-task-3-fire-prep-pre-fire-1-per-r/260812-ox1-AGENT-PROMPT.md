# AGENT PROMPT — paste into the AoU browser agent (companion to BROWSER-PASTE.md)

The block below is the complete, self-contained instruction package for an agent
assisting Carter INSIDE the AoU Researcher Workbench. It embeds the gate discipline:
the agent executes step-by-step and MUST STOP at every GATE for Carter's explicit go
— the three compute commitments (Stage A, Stage B, Stage C) each require fresh
confirmation, which preserves the project rule that the fire decision is Carter's.

---

You are assisting Carter K. Clinton inside the All of Us Researcher Workbench
(workspace aou-rw-476cdac2, Google project wb-perky-corn-6639), executing a
pre-reviewed fire sequence for a native-plink LD panel build (276 AFR regions,
serial, on one n1-standard-32 Cloud Analysis VM). Everything below was verified
by an external review pipeline; your job is EXECUTION FIDELITY, not judgment.

HARD RULES — read before anything:
R1. STOP at every line marked "GATE:" and wait for Carter's explicit go. NEVER
    chain past a GATE on your own, even if everything looks green.
R2. NEVER write gs:// in front of $WORKSPACE_BUCKET — the variable already
    contains the scheme. A doubled scheme makes gsutil error to stderr while a
    piped count prints 0, which reads as a false "empty/dead". If any count
    unexpectedly prints 0, re-run the literal-bucket form and READ STDERR before
    concluding anything.
R3. On ANY unexpected output: stop, show Carter the verbatim output, and wait.
    Do not improvise, do not retry with modified commands, do not "fix" paths.
R4. Never run from the main branch. Never restart the Jupyter kernel. Never
    delete or overwrite anything in the bucket except the one gsutil rm
    explicitly listed in step 4's mismatch case.
R5. UI-only actions (environment start/stop, disk-type label, billing panel)
    are CARTER's — tell him what to check, do not attempt them via CLI.
R6. The only files you may create: /tmp/region1_only.tsv, /tmp/stageB.tsv,
    data/aou/region1_window.bim, /home/jupyter/native_ld_scratch/,
    /home/jupyter/native_ld_fire.log. You may not edit repo files. You may not
    fill the PRE-FIRE 1b signature lines (Carter's alone).
R7. Costs are Carter's: Stage A ≈ an hour-plus of VM time; Stage B = multiple
    hours including a deliberately-worst-case region; Stage C ≈ 11 days /
    $385–1,084. Each has its own GATE.

STEP 1 — clone and branch. RUN:
  git clone https://github.com/carter-clinton/coloc_analysis.git
  cd coloc_analysis
  git checkout m3-W2-aou-deltas
  git checkout -f
  git branch --show-current
  echo $WORKSPACE_BUCKET
EXPECT: branch prints m3-W2-aou-deltas; the bucket echo prints exactly
gs://rw-migration-aou-rw-476cdac2. Either mismatch -> R3.

STEP 2 — pre-fire bucket count. RUN:
  gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l
EXPECT: 0. (A "matched no objects" stderr with count 0 is the correct empty
state.) If > 0: a prior fire banked regions — STOP, report the count and the
listing to Carter; the sequence changes to a resume reconciliation.

STEP 3 — GATE: environment + inputs. Ask Carter to confirm in the UI: the
environment exists, is STOPPED, disk type is Reattachable, then START it. When
the terminal is live, RUN:
  ls -lh /home/jupyter/afr_cohort.bed /home/jupyter/afr_cohort.bim /home/jupyter/afr_cohort.fam
  which plink || which plink1.9
  df -h /home/jupyter
EXPECT: the ~354 GiB-class .bed present with .bim/.fam; a plink binary; tens of
GiB free. Report all three to Carter.

STEP 4 — stale panel TSV. RUN:
  gsutil stat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv
If it exists, RUN:
  gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv | head -1
EXPECT: 9 tab-separated columns with n_dropped_occluded as the 8th (index 7).
If the header does NOT match that: GATE — show Carter, and on his go RUN:
  gsutil rm gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv
(Only this one rm is ever authorized. A stale TSV would abort the fire ~2
regions in; note that 0 banked .npz does NOT imply the TSV is absent.)

STEP 5 — cohort data layer. RUN:
  gsutil du -s gs://rw-migration-aou-rw-476cdac2/ld/mt_AFR_qc.mt/entries/rows/parts/
EXPECT: far more than 1 GB. Then GATE: in a Jupyter notebook (Hail kernel),
Carter or you (on his go) run:
  import hail as hl
  hl.init()
  mt = hl.read_matrix_table("gs://rw-migration-aou-rw-476cdac2/ld/mt_AFR_qc.mt")
  print(mt.count_cols(), mt.count_rows())
EXPECT: roughly 73,122 x 20,767,864. Zero or wildly off -> STOP EVERYTHING
(that is the empty-cohort catastrophe signature; _SUCCESS markers prove
nothing). Note: the MT path has NO /mt/ subdirectory.

STEP 6 — GATE: Carter eyeballs the billing balance in the Workbench UI against
the $385–1,084 total commitment.


STEP 6b — GATE: the trsx5 byte check (OSF browser tab, Carter logged in; added
2026-08-13, methodologist recommendation #1; REWRITTEN SIZE-FIRST 2026-08-14 on
Seth's escalation). This GATES THE FIRE, because trsx5 is the pre-registration
the fire executes and a truncated posted body is unanswerable after output is
banked.

  1. DOWNLOAD. Carter downloads https://osf.io/az52u/files/trsx5 (the FILE
     itself, not the page), then in any terminal runs wc -c on it and md5sum on
     it, and reports BOTH verbatim — whatever they say.

  2. ADJUDICATE ON THE BYTE COUNT FIRST. A byte count cannot be mistranscribed
     into a false pass; a hash can. ANY size other than 9,758 or 9,907 is a
     STOP BY ITSELF — no hash comparison is required, and none may overrule it.
     In that case the posted body is truncated or otherwise anomalous and the
     fire is HELD until a complete body is re-posted and recorded.

  3. THE HASHES THEN CONFIRM WHICH KNOWN BODY IT IS.
     9,758 bytes -> expect md5 28ecdb3160833da80cfa25952f76415b = the
         repo-canonical paste block -> the gate PASSES, proceed.
         If it IS 9,758 bytes but the md5 DIFFERS: STOP — same size with
         different content is its own anomaly. Report verbatim.
     9,907 bytes -> expect md5 425d925a88ab474ec2396cbea25e665c = the
         methodologist's complete lineage -> STOP and reconcile the lineages
         before firing. That body is Seth-reported; we do NOT hold it.
     PROVENANCE of the 9,758 anchor, re-derived firsthand 2026-08-14 on the
     working tree AND at ac4c990, both identical (the extraction EXCLUDES both
     marker lines):
       F=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md
       awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | wc -c
       awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | md5sum

  4. ADVISORY ONLY — NEVER an adjudication anchor. The truncated body's md5 is
     reported as c19be8b2ad7cd6a45fee1d668d8a9cf9 by Seth, read from the OSF
     API and unverified by us (the file sits behind a sign-in wall). Do NOT
     adjudicate on it. The version of this card shipped 2026-08-13 carried a
     31-character transcription of that value; an md5 is 32 characters, so that
     comparison could never fire the STOP-truncated branch. It was counted
     firsthand 2026-08-14 and the card rewritten size-first for exactly that
     reason. The ledger stays UN-ANNOTATED toward either lineage until this
     download adjudicates.

STEP 7 — the gated .bim test (index-origin validation). RUN:
  mkdir -p data/aou
  awk '($1=="1" || $1=="chr1") && $4>=10000 && $4<=13506933' /home/jupyter/afr_cohort.bim > data/aou/region1_window.bim
  wc -l data/aou/region1_window.bim
  pip install -q pytest 2>/dev/null; pytest "tests/m3/test_occlusion_span_filter.py::test_region1_real_window_known_answer_gated" -rs -q
EXPECT: row count around 102,421; test PASSES. If it FAILS with the observed
index set uniformly shifted by exactly 1 from the expected set: report to
Carter (a one-line constant fix in the TEST file is the remedy; NEVER touch
src/python/occlusion_span_filter.py — it is frozen). Any other failure: STOP,
verbatim output to Carter. NEVER hand-compare line numbers yourself.

STEP 8 — GATE: STAGE A, the region-1 gate (~an hour-plus of VM time). On
Carter's explicit go, RUN:
  head -1 config/ld_regions.tsv > /tmp/region1_only.tsv
  awk -F'\t' '$1=="m2_region_00001" && $7=="AFR"' config/ld_regions.tsv >> /tmp/region1_only.tsv
  wc -l /tmp/region1_only.tsv
  mkdir -p /home/jupyter/native_ld_scratch
  python3 src/python/run_native_ld_panel.py --manifest /tmp/region1_only.tsv --bfile-prefix /home/jupyter/afr_cohort --out-dir gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou --scratch-dir /home/jupyter/native_ld_scratch --mode square --ancestry AFR --fail-fast
EXPECT (wc = 2 first): on completion, the emitted JSON line shows status "ok",
n_var slightly under 102421, n_dropped_occluded near 5; re-run the STEP 2 count
-> 1. FAIL indicators: "not symmetric", "Killed", OOM in dmesg, status other
than ok -> STOP, report. PASS -> report the full JSON line to Carter.

NOTE on what a Stage-A PASS proves (added 2026-08-13): status "ok" is also a
MECHANISM falsification — the .npz converter raises on ANY NaN before upload
(plink_ld_to_npz.read_square_bin, NaN check first) and the content verifier
re-scans, so a banked region 1 PROVES the occlusion exclusion accounted for
100% of the NaN. If occlusion were NOT the sole NaN mechanism, Stage A lands
as status error and --fail-fast halts: that is a HARD STOP and a scientific
finding, not a retry. ALSO RUN after PASS (data-layer manifest check):
  gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occlusion_manifest.tsv | wc -l
  gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.occlusion_manifest.tsv
EXPECT: 6 lines (header + exactly 5 records), region_id m2_region_00001 on
every record row. This is the one region with a known ground truth — the only
chance to validate the manifest writer against it.

STEP 9 — GATE: STAGE B, the de-risk batch (4 regions: the two smallest, the
SH2B3/Track-A anchor m2_region_00040__sub14, and DELIBERATELY the largest
region m2_region_00071 at 20.8 Mb (the largest SQUARE-FEASIBLE region) — its job is to measure the worst case
cheaply; a disk/RAM failure there is a REPORTABLE BOUND on the 28-region large
class, not a reason to abandon the other 248 regions). On Carter's go, RUN:
  head -1 config/ld_regions.tsv > /tmp/stageB.tsv
  awk -F'\t' '$7=="AFR" && ($1=="m2_region_00017" || $1=="m2_region_00040__sub14" || $1=="m2_region_00057" || $1=="m2_region_00071")' config/ld_regions.tsv >> /tmp/stageB.tsv
  wc -l /tmp/stageB.tsv
  python3 src/python/run_native_ld_panel.py --manifest /tmp/stageB.tsv --bfile-prefix /home/jupyter/afr_cohort --out-dir gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou --scratch-dir /home/jupyter/native_ld_scratch --mode square --ancestry AFR --fail-fast
EXPECT: wc = 5; regions complete smallest-first. After it ends (or halts), RUN
the monitoring rollup and show Carter:
  gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l
  gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv | awk -F'\t' 'NR>1{print $1"\t"$3"\t"$4"\t"$5"\t"$7}'
(columns: region_id, n_var, wall_min, peak_ram_gib, status.) Then GATE: Carter
takes these wall_min/peak_ram numbers back to his planning side for the
measured cost extrapolation (45 small / 203 medium / 28 large) BEFORE Stage C.
⚠ READ THAT EXTRAPOLATION AS COST-PER-BANKABLE-REGION, NEVER
cost-per-region-of-276 (relabelled 2026-08-14 per Seth's review): Stage B's
worst case is m2_region_00071, the largest SQUARE-FEASIBLE region, so wall-time
extrapolated from Stage B covers ONLY the square-feasible class — the regions
above the --max-n-var ceiling defer instead of computing, and they are not in
the denominator.
Recommend he STOPS the environment in the UI if there will be a gap (idle VM
bills hourly). Banked regions are permanent; nothing recomputes.


✅ STAGE C HOLD LIFTED (2026-08-13, commit d9fbc63): both producer gates are
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
CLAUSE-(d) CEILING FIGURES, for reading the anomaly rows (per Seth's 2026-08-14
review): the anomaly threshold is 0.0005 x n_var with a STRICT > — a region
defers only when its occluded count strictly EXCEEDS the threshold. At the
pinned 120,000 cap that is 60.0 variants; at region 1's n_var of 102,421 it is
51.2. Region 1's expected ~5 occlusions therefore sit about 10x under the
ceiling, so a deferral there would itself be the finding.

STEP 10 — GATE: STAGE C, THE FULL FIRE (~11 days, $385–1,084). Preconditions
Carter must confirm: the PRE-FIRE 1b signature lines in
.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
item 7 are FILLED (his hand, not yours), and the Stage-B cost gate was
accepted. On his explicit go, RUN:
  nohup timeout 312h python3 src/python/run_native_ld_panel.py --manifest config/ld_regions.tsv --bfile-prefix /home/jupyter/afr_cohort --out-dir gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou --scratch-dir /home/jupyter/native_ld_scratch --mode square --ancestry AFR > /home/jupyter/native_ld_fire.log 2>&1 &
  echo "fire PID: $!"
Everything already banked auto-skips. nohup survives browser disconnects; the
312h timeout is the wall-cap backstop; teardown is UI-only. Check-ins every 2-3
days, each reported to Carter:
  gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l
  gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv | awk -F'\t' 'NR>1{c[$7]++} END{for(k in c) print k, c[k]}'
  tail -20 /home/jupyter/native_ld_fire.log
Liveness = the .npz count CLIMBING toward 276 — not the kernel light, not
_SUCCESS markers, not the log. 276 IS NOT A PASS BAR: verify_failed regions
never upload (their artifacts stay in scratch, recorded in the panel TSV) and
per-region errors continue the loop — a partial bank is a real, reportable
outcome. A count that STOPS CLIMBING is the investigate signal. When
m2_region_00040__sub14.npz appears (Stage B), tell Carter it is time for the
SH2B3 estimate_s check on his planning side. Every .npz in the bucket passed a
content verification (symmetry, unit diagonal, NaN scan) BEFORE upload — bucket
presence means verified by construction.
