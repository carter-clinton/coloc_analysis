# PENDING PASTE — fire morning 2026-08-19, resume artifact

Carter left to teach mid-hold. This is the EXACT ruling block that was composed but
NOT YET PASTED to the AoU browser agent. On resume: Start the app in the UI (that
completes the required OS-update reboot if it was Stopped for the gap — in that
case the reboot sequencing inside the block is ALREADY satisfied and the agent
should go straight to the post-reboot re-checks), then paste the block below to the
agent verbatim.

Sequence position at close: STEPs 1-4 done and green (adjudications recorded in
HANDOFF/STATE); STEP 5 Part 2 hit an R3 stop — `UnsupportedFileSystemException: No
FileSystem for scheme "gs"` (no GCS connector on this VM's local Spark; no Hail
kernel on the Cloud Analysis VM class; count never ran; NOT a data verdict). The
block below issues the substitute gate.

--- PASTE FROM HERE ---

Ruling on the STEP 5 Part 2 stop: correct stop, and the diagnosis is accepted — no
GCS connector on this VM's local Spark; the count never ran; NOT a data verdict.
We will NOT improvise Spark/connector fixes on the fire path (the Spark 3.5.6 and
Java 17 warnings reinforce that). The Hail-kernel assumption in the card is an
environmental error in the RUNBOOK, recorded as a ruled deviation.

SUBSTITUTE GATE — same question ("is the cohort empty?"), more direct evidence,
because the fire's ACTUAL input is the staged bfile, not the MT:

  (i) Count the fire's real substrate, locally:
        wc -l /home/jupyter/afr_cohort.bim /home/jupyter/afr_cohort.fam
      EXPECT: .bim ~= 20,767,864 and .fam ~= 73,122. These are the same cohort
      dimensions STEP 5 was after, measured on the input the fire actually reads.
      Wildly off (either one) -> STOP EVERYTHING.

  (ii) GCS-side corroboration WITHOUT Spark — read Hail's own metadata:
        gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt/
        gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt/rows/
      then locate the metadata.json.gz for the rows and cols component tables and:
        gsutil cat <that metadata.json.gz> | gunzip | python3 -c "import json,sys; d=json.load(sys.stdin); pc=d.get('partitionCounts'); print(len(pc) if pc else None, sum(pc) if pc else 'partitionCounts ABSENT')"
      EXPECT: rows sum ~= 20,767,864; cols sum ~= 73,122. If partitionCounts is
      absent from the metadata, report that and rely on (i) plus the already-
      measured ~1.6 TB of entry parts — do not force it.

  The gate PASSES on (i) matching expectations, with (ii) as corroboration.
  Leave the failed notebook exactly as it is (cell [1] with the error IS the
  record); no kernel restarts, no retries of the Hail read.

CONTEXT, read-only, on my go now: cat ~/load-env.sh (and ~/load-env if distinct)
and paste them — June-era setup context for the record only; the gate does not
wait on or depend on them.

THEN, after the substitute gate passes — the reboot sequence: the environment
panel shows "Reboot is required for OS update." Carter will Stop -> Start the app
in the UI BEFORE STEP 7 — we will not begin an ~11-day fire on a VM with a pending
OS update, and a mid-fire forced reboot would kill the nohup loop. This is NOT an
R4 violation: it is a deliberate whole-VM reboot between steps with nothing
running. The disk persists across Stop/Start. (If Carter already Stopped the app
for the teaching gap and Started it on return, this reboot is ALREADY DONE — skip
to the re-checks below.)

After the VM is back, BEFORE proceeding, re-verify and paste verbatim:
  ls -lh /home/jupyter/afr_cohort.bed /home/jupyter/afr_cohort.bim /home/jupyter/afr_cohort.fam
  which plink || which plink1.9
  df -h /home/jupyter
  cd ~/coloc_analysis && git branch --show-current && git status --short | head -5
EXPECT: identical to the earlier STEP 3 result; branch m3-W2-aou-deltas. Any
change -> STOP and report.

Then hold for Carter's STEP 7 go. Disk-type ruling for the record: treated as
Standard — this environment is NEVER deleted, only stopped, for the life of this
panel build.

--- PASTE ENDS HERE ---
