# Debug seed — genome-wide rebuild wedges at `count_cols` (Py4J mutual-wait)

**Status:** OPEN — seeded, not yet investigated. Open with `/gsd-debug` next session.
**Branch/HEAD:** `m3-W2-aou-deltas` @ `997461b` (no code changed this session).
**Cluster:** torn down → $0. Investigation needs ONLY artifacts + code, not a live cluster.

## Symptom
Production `AOU-1_template.ipynb` genome-wide rebuild deterministically freezes in Cell 3
`load_qc_cohort`, immediately after it prints `state=FRESH ancestry=afr`. Reproduced identically on two
clean fires: YARN apps `application_1780701402498_0003` and `_0004`. No Spark stage launches
(`stage=0`), no executors register, `/tmp/hail.log` freezes right after a `SizeEstimator`
reflective-access warning flood.

## Settled facts (direct thread evidence, not inference)
- Hail is lazy: `read_matrix_table(mt_path)` is cheap and PASSES. The freeze is at the **first action**,
  `count_cols`, which materializes the genome-wide plan.
- **Driver JVM:** no `is.hail.*` / GoogleHadoopFileSystem / executor-task thread is RUNNABLE. Every
  RUNNABLE thread is an idle `sun.nio.ch.EPoll.wait` loop. Py4J uses `ClientServerConnection`
  (single-threaded callback mode) and **both** connection threads sit in
  `ClientServerConnection.waitForCommands` (idle). `main` is in `PythonGatewayServer$.main →
  FileInputStream.readBytes` on stdin = the liveness watcher (red herring; not the command path). CPU flat.
- **Python kernel:** main/execution thread in **untimed `recvfrom`** on the Py4J gateway socket
  (Cell 3 `exec_count=None` → still running). A leaked `CLOSE-WAIT` socket to the controlled-tier PSC
  endpoint and an idle `gcs-async-channel-pool-0` thread parked in `Object.wait()` are BOTH idle
  artifacts (chased + dismissed during diagnosis).
- ⇒ Mutual wait at the Py4J boundary.

## Ruled OUT
slow driver plan (no `is.hail` CPU burn) · GCS read/write hang · requester-pays (CUSTOM made no
difference; orthogonal) · any Spark/GCS config knob · Py4J heartbeat/timeout desync (Py4J has no default
read timeout — untimed `recvfrom` is the normal "call in progress" posture).

## Hypotheses to test
- **H1 — stdout/stderr pipe-buffer deadlock.** `SizeEstimator` warning flood right before freeze fills
  the JVM→kernel log pipe faster than ipykernel drains it; JVM blocks on the full pipe, Python waits
  forever. Masked at chr22's smaller log volume. **Discriminator NOT yet run:** is any JVM thread
  blocked in `FileOutputStream.write`/`writeBytes` to the log/stderr fd? (Note: prior sweep found no
  such write-blocked thread — weak evidence *against* H1, but the sweep wasn't exhaustive.) Cheap test:
  small synthetic genome-scale MT + `count_cols` with log4j at WARN flooding stderr through the kernel.
- **H2 — Py4J lost-response.** Action's Java call returned but response not delivered → no `is.hail`
  thread remains yet Python waits. Test: instrument/trace the Py4J call boundary on a small repro.

## Lead fix (mechanism-agnostic — pursue regardless of H1/H2)
**Per-chromosome checkpoint loop.** Bound each action the way `interval_filter="chr22"` did in Gate-C
(which never wedged): loop chromosomes, filter→QC→checkpoint per chrom, union. **KEY CLUE:** the ONLY
variable differing from the passing Gate-C run is `interval_filter=None` (full autosomal partition
count the first action must materialize). This also slashes per-action log volume if H1 is real.
Design + cost this in `/gsd-debug` (or `/gsd-plan-phase`) before re-provisioning a cluster.

## Forensics (banked; Track-1 evidence, do NOT delete)
`gs://rw-migration-aou-rw-476cdac2/ld/_forensics/`: `hail_0003_py4j_desync.log`,
`hail_0004_py4j_mutual_wait.log`, `jstack_0003_98900_py4j_desync.txt`, `jstack_0004_a.txt`,
`jstack_0004_b.txt`.

## Process lesson (4 misattributions before resolution)
both-idle → JVM-upload-hang → Python-controlled-socket → upload-pool-handoff, each "decisive" and each
overturned by the next sample. `CLOSE-WAIT` sockets + `Object.wait()` pool threads are idle artifacts;
the arbiter is the thread actually servicing the call. A quiet log + flat CPU looks identical to a wedge
during an I/O/plan phase — see `[[feedback_aou_hail_driver_quiet_vs_wedge]]`.
