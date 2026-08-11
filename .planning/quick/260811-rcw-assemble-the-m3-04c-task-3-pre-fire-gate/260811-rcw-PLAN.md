---
phase: quick-260811-rcw
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.log
  - .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.tsv
  - .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PRE-FIRE-GATE-REVIEW.md
autonomous: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - QUICK-260811-RCW

must_haves:
  truths:
    - "Carter can read ONE document and see, for every gate that bears on the ~11-day / $385-1,084 fire, its CURRENT status, the command or artifact that produced that status, the date of that evidence, and what would change it."
    - "Where the three layered records disagree (HANDOFF.json's gates block, m3-04c-BLAST-RADIUS.md's gate binding, the aou-ld-pipeline skill's older Wave-2 gate sequence), the divergence is STATED and resolved BY RECENCY with the newer record named as the winner. Nothing is silently merged. This includes the divergences INSIDE HANDOFF.json itself, whose narrative gate rows are frozen at their writing date while blast_radius_gate_ledger and suite_baselines are current."
    - "Every local claim in the review names the command that produced it, and that command's real output is on file in the same directory (260811-rcw-evidence.log), so no number in the review rests on a recollection."
    - "Every perimeter-only fact is labelled LAST-KNOWN with its date, and carries the exact in-perimeter command Carter runs at gate time plus that command's expected result. None is presented as a current measurement."
    - "The fire's liveness arbiter is stated as the GCS .npz object listing climbing to 276 -- explicitly NOT the kernel light and NOT a _SUCCESS marker."
    - "The Carter-only sequence (PRE-FIRE 1 / 1b / 2 / 3 -> STEP A region-1 gate -> STEP B the billed fire -> STEP C-G egress and hand-back) is present and faithful to m3-04c Task 3, carries the cost band, and carries the standing rule that AN AGENT MUST NEVER FIRE IT."
    - "Every open item is classified explicitly as BLOCKS-THE-FIRE or BOUNDS-WHAT-THE-OUTPUTS-CAN-BE-USED-FOR, with a one-line reason. Most bound usage; the review says so precisely rather than lumping them together as 'open'."
    - "The review carries exactly ONE unhedged fire-readiness verdict line, in one of two fixed forms, and that line is derived from the evidence TSV rather than asserted."
    - "The review carries its own scope statement: local evidence only, perimeter state is last-known and gate-time-checkable, and nothing in the document fires or authorizes anything."
    - "ZERO perimeter contact was made and ZERO files outside the quick directory were modified, and both are checkable after the fact rather than promised."
  artifacts:
    - path: ".planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.log"
      provides: "Raw, verbatim transcript of every local verification command and its real output, one block per check_id. The substrate every number in the review is reconciled against."
      min_lines: 80
    - path: ".planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.tsv"
      provides: "Machine-readable checklist: check_id, area, what, command, expected, observed, verdict, evidence_date"
      contains: "check_id"
    - path: ".planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PRE-FIRE-GATE-REVIEW.md"
      provides: "The single current-state surface Carter reads before deciding whether to fire: scope statement, verdict, reconciled gate table, local re-verification results, perimeter-only gate-time checks, the Carter-only sequence, and the BLOCKS-vs-BOUNDS open-items table."
      min_lines: 180
      contains: "VERDICT"
  key_links:
    - from: "260811-rcw-PRE-FIRE-GATE-REVIEW.md"
      to: "260811-rcw-evidence.tsv"
      via: "every local claim cites its check_id"
      pattern: "L-[0-9]{2}"
    - from: "260811-rcw-evidence.tsv"
      to: "260811-rcw-evidence.log"
      via: "one log block per check_id, command recorded verbatim"
      pattern: "#{5} L-[0-9]{2}"
    - from: "260811-rcw-PRE-FIRE-GATE-REVIEW.md"
      to: ".planning/phases/m3-aou-afr-ld-panel-build/m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md"
      via: "the Carter-only sequence reproduces Task 3's PRE-FIRE and STEP labels"
      pattern: "PRE-FIRE 1b"
    - from: "260811-rcw-PRE-FIRE-GATE-REVIEW.md"
      to: ".planning/HANDOFF.json"
      via: "gate table rows name their source record and its date"
      pattern: "HANDOFF"
---

<objective>
Assemble the m3-04c Task 3 PRE-FIRE GATE REVIEW: a single current-state surface Carter
reads before deciding whether to fire the ~11-day / $385-1,084 billed AoU loop.

This task VERIFIES AND COLLATES. It fires nothing, decides nothing, and authorizes nothing.

Purpose: the fire's readiness is currently spread across four records written on four
different dates, two of which contradict each other and one of which (the skill's Wave-2
gate sequence) describes a producer that was killed and replaced. Carter should not have
to perform that reconciliation in his head at the moment he is deciding whether to spend
~$1,000 and eleven days.

Output: one review document, backed by a machine-readable evidence TSV and a verbatim
command log, all three confined to this quick directory.
</objective>

<absolute_constraints>
⛔⛔ **AN AGENT MUST NEVER FIRE THE BILLED LOOP.** Not this one, not any. The fire is
Carter's terminal gate ($385-1,084, ~11 days). This is a standing project rule
(`.planning/HANDOFF.json` `do_not[0]`), not a scoping preference for this task.

⛔⛔ **ZERO PERIMETER CONTACT OF ANY KIND.** Do not run `gsutil`, `gcloud`, `bq`, or `wb` —
not even read-only control-plane calls, not even `wb workspace list`, not even
`gsutil ls`. Do not start, restart, resume, stop or describe any cluster or VM. Do not
open the AoU Workbench. Every perimeter fact in the review is LAST-KNOWN, sourced from
the in-repo records, and handed to Carter as a gate-time command for HIM to run.

⛔ **NO SOURCE, TEST, OR CONFIG CHANGES.** `src/`, `tests/`, `config/`, `Snakefile` and
`.planning/DECISIONS.md` are read-only for this task. The one permitted exception is
restoring `tests/m3/sparse_parent_benchmark.tsv` with `git checkout --` after the suite
run rewrites its timing columns (a known, documented jitter artifact — see
`.planning/HANDOFF.json` `prep_landmines`). Nothing else may be checked out, reverted,
or edited.

⛔ **ALL WRITES CONFINED TO** `.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/`.

⛔ **NO `git add -A` / `git add .`** on this GPFS tree. Explicit paths only.

Everything in this plan is NC-State local, read-only, and **$0**.
</absolute_constraints>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/HANDOFF.json
@.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-BLAST-RADIUS.md
@.claude/skills/aou-ld-pipeline/SKILL.md

Read, at the points named in the task actions (not all up front):
- `.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md`
  lines **1302-1536** — Task 3, the terminal gate. This is the SOURCE OF TRUTH for the
  Carter-only sequence. Reproduce its structure faithfully; do not paraphrase away its
  warnings. (The file is ~1,650 lines; do not read it whole.)
- `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` — E-2 (decided as A,
  three obligations undischarged), E-3, E-4, K-2 (declined), K-3 (closed).
- `.planning/DECISIONS.md` lines **1014-1036** (`DEC-2026-08-05-m3-ld-read-path` — the
  BLOCKER-1 remedy and its acceptance test) and the
  `DEC-2026-08-07-e2-orientation-disposition` entry near line 1173.
- The two sibling quick directories, for the state of the undischarged obligations:
  `.planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/` (E-2 drafts:
  manuscript limitation, OSF entry, framing decision surface) and
  `.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/` (the SR4-OPEN
  dossier). Read their `-SUMMARY.md` only — you need their STATE, not their contents.

<interfaces>
Verified firsthand at planning time, 2026-08-11, HEAD `be1ee64`. All read-only, $0.

--- ENVIRONMENT ---
    python/pytest:  /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest
    snakemake:      /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
                    (never the miniconda3 base — Python 3.13; Snakemake 7.32.4 needs 3.11)
    repo root:      /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

--- SUITE BASELINES (.planning/HANDOFF.json suite_baselines, 2026-08-07) ---
    tests/m3       902 passed / 31 skipped / 0 failed     (~14 min)
    tests/phase2   136 passed /  1 skipped / 0 failed     (~2 s)
    ⚠ THE RULE, verbatim from that record: "Skips must STAY at 31 and 1. A new test
      landing as a SKIP is NOT evidence — check the skip count, not just the failure
      count."
    ⚠ HEAD has moved since the baseline was taken (`b02707a` -> `be1ee64`). The four
      intervening commits (`500002d`, `b945c59`, `f78bbc1`, `399c50f`, `2b13dce`,
      `be1ee64`) are the 260811-pmv docs arc. A passed count that is NOT 902 is a claim
      to RECONCILE against those commits in the review, not a number to quietly adopt.
      A skip count that is not exactly 31 / 1 is a RED.

--- CONFIG AS SHIPPED (config/pipeline.yaml, verified at planning time) ---
    :369-373  ld_read_path:  enabled: true
                             ancestries: [AFR]
                             allele_aware: true
                             coloc: true
    :255      strict_aou_only: false        (under the ld_panel block)
    :393      m3_convert_max_n_var: 120000
    :295      allow_degraded: false
    ⚠ `allow_partial_manifest` was NOT found as a config key at planning time; its
      default lives in `src/python/assemble_occlusion_catalog.py` (False, the GATE 1
      raise at :415-431). Record BOTH facts — the config value if present, otherwise the
      code default and where it lives. Do not report an absent key as `false` without
      saying where the `false` came from.

--- THE BLOCKER-1 ACCEPTANCE PROPERTY AND ITS ENFORCERS ---
    The property (DEC-2026-08-05-m3-ld-read-path, verbatim): "prove resolved ==
    what-the-script-opens — grep the rule's shell: for {input.ld_matrix}, then assert the
    R script opens that exact path. A green DAG is NOT evidence."

    Live wiring:  src/snakemake/rules/finemap.smk:449   --ld-file {input.ld_matrix} \
    Guard rail :  the params.region_id line must survive character-for-character.

    TWO enforcing suites, and the review must name BOTH and state what each does and
    does NOT prove:
      tests/m3/test_ld_read_path.py    — the DEC-2026-08-05 acceptance test.
        :251 test_run_finemap_shell_passes_the_declared_ld_matrix       (static)
        :277 test_ld_file_option_is_declared                            (static)
        :306 test_loader_opens_the_declared_file_not_the_reconstructed_path  (BEHAVIOURAL)
        :335 test_absent_ld_file_still_reconstructs_from_ld_dir              (BEHAVIOURAL)
        :356 test_ld_file_works_when_ld_dir_is_absent                        (BEHAVIOURAL)
        :389 test_both_absent_returns_the_byte_identical_legacy_status       (BEHAVIOURAL)
        :497 test_declared_and_opened_paths_are_both_recorded_in_the_output_json
        ⚠ THIS SUITE STILL PINS `MIN_LD_OVERLAP <- 1L` AT :186. That is NOT the
          un-remediated BLOCKER-A defect: :180-182 documents that the loader-functions-only
          harness cuts the source above the real thresholds, and explicitly delegates
          production acceptance thresholds elsewhere. Say this plainly. The blast radius's
          "the gate is disabled in all 8 of them" sentence is TRUE OF THIS FILE and is NOT
          the current state of the property, because —
      tests/m3/test_ld_declared_authoritative.py — "THE PRODUCTION-THRESHOLD ACCEPTANCE
        SUITE for the m3-04c blast radius" (:3). It READS the thresholds from
        config/susie_policy.yaml (:76-81, "read, never hardcoded") and exercises
        assert_declared_ld_authoritative(). This is the BLOCKER-A remediation
        (quick-260805-23d, 51a60ca + ab19186).
      ⚠ The m3-r-ld conda env at /rs1/researchers/c/ckclinto/conda_envs/m3-r-ld is the
        marker that makes the BEHAVIOURAL tests RUN rather than skip. If any of the four
        behavioural tests SKIPS, that is a RED, not a pass — a skipped assertion is not
        evidence ([[feedback_skip_guard_masks_not_fixes]]).

--- THE CONVERT DAG ---
    rule m3_convert_aou_afr_rds_all   src/snakemake/rules/m3_convert_npz_rds.smk:290
    Aggregate target, 276 AFR ids DERIVED from config/ld_regions.tsv (153 whole + 123
    __sub). Expected: a clean 575-job DAG (HANDOFF headline_2026_08_05d_PRIOR).
    ⚠ THIS IS A TARGETED DRY-RUN AND IS SATISFIABLE. Do NOT confuse it with the
      FULL-WORKFLOW `snakemake --dry-run --quiet`, which is STRUCK as unsatisfiable
      pre-fire (D-04b-03 / MEDIUM-7: `data/processed/ld_reference/` does not exist, so
      resolve_ld_path RAISES). The full-workflow substitute is `--list`. The review must
      make that distinction explicit, because a reader who knows MEDIUM-7 will otherwise
      think a struck check is being run.
    ⛔ If any check tempts you to `touch` a fake `.rds` or `mkdir` an absent data
      directory to make something pass: STOP and record it as a RED.

--- LOCAL DATA STATE (expected, pre-fire) ---
    data/processed/ld_reference           DOES NOT EXIST   (verified at planning time)
    data/interim/aou_ld_exports/AFR_aou/*.npz              expect 0
    .planning/phases/m3-aou-afr-ld-panel-build/validation/ 4 subdirs, .gitkeep only
                                                           (the 4-check protocol has
                                                           NEVER been run)

--- THE THREE LAYERED RECORDS, WITH THEIR DATES ---
  (a) .planning/HANDOFF.json                        2026-08-07  ← most recent
        `gates` (narrative, per-row, frozen at each row's own writing date)
        `gates.blast_radius_gate_ledger` (current as of 2026-08-07)
        `suite_baselines`, `cluster`, `data_state`, `do_not`, `carter_decisions_outstanding`
  (b) m3-04c-BLAST-RADIUS.md  §"Gate binding — what blocks what"   2026-08-05
  (c) .claude/skills/aou-ld-pipeline/SKILL.md  §"Wave 2 gate sequence"  PREDATES the arc

  ⚠⚠ KNOWN DIVERGENCES THE REVIEW MUST STATE EXPLICITLY (do not silently merge; resolve
  by recency with the winner NAMED):

  1. INSIDE (a), the file contradicts itself. `gates.panel_reachability` still reads
     "⛔ OPEN AND DEEPER THAN DIAGNOSED ... CARTER'S DECISION" and
     `gates.blocker1_ld_read_path` reads "✅ DECIDED ... ⛔ NOT YET IMPLEMENTED" — both
     frozen at 2026-08-04/05. They are SUPERSEDED within the same file by
     `blast_radius_gate_ledger` ("the ~11-day billed fire: CLEAR on A/B/C"),
     `blocker_a_ld_file_authoritative` ("✅ CLOSED"), `blocker_c_nothing_builds_the_rds`
     ("✅ CLOSED") and `completed_this_session`. Recency wins.
  2. INSIDE (a), `gates.m3_04c` quotes "Suite 548P/31S/0F" while `suite_baselines` in the
     same file says 902/31/0. The 548 figure is the 2026-08-05 snapshot. Recency wins.
  3. (c) DESCRIBES A PRODUCER THAT WAS KILLED. The skill's GATE 2 / GATE 3 are the Hail
     BlockMatrix Path-A.3 fire: the A.3 lowering hang, CR-01's ~2 TB dense-scratch
     ordering question, "full 322-cell production + 44 egress", "Egress = 44 export
     requests (22 chr x 2 anc)", and the atomic-final-write Phase 2. That producer was
     re-scoped away; the current producer is `src/python/run_native_ld_panel.py` —
     native plink1.9, Hail-free, ONE stopped VM, AFR-only, **276 regions**, writing
     per-region `.npz` DIRECTLY to `gs://<bucket>/ld/AFR_aou/`, with egress redefined as
     **at most 22 AFR chromosome groups plus size splits** (m3-04c must_haves; the
     egress-unit redefinition is recorded in
     `.planning/amendments/m3-egress-and-validation-protocol-addendum.md`). So CR-01,
     the A.3 hang, "322 cells" and "44 bundles" are SUPERSEDED and must not be presented
     as live blockers.
     ⚠ BUT the skill's GATE 0 (egress classification, RULED PASS 2026-04-28) and GATE 1
     (CDR pin v8 + cost/credit, CLEARED 2026-06-12) and GATE 1.5 (cohort rebuild, DONE)
     are STILL LIVE AND STILL VALID. Do not throw the whole skill table out because part
     of it is stale — that is the failure this reconciliation exists to prevent.
  4. (b)'s gate-binding row for the fire names BLOCKER-A, BLOCKER-C and BLOCKER-D. A and
     C were closed by quick-260805-23d; D is PARTIAL. (a) is the winner.

--- EVIDENCE DISCIPLINE (project-specific, non-negotiable) ---
  * A COUNT IS A CLAIM. `grep -r` does NOT follow symlinks — `results/legacy/region_analysis`
    IS a symlink into /rs1 — and `grep -R` from the repo root silently over-counts. This
    project got the same count wrong FOUR times (1,957 -> 44 -> 1,944 -> 1,909). Scope
    every count, and reconcile it arithmetically before it ships.
    [[feedback_a_count_is_a_claim_scope_and_reconcile]]
  * ⚠ DO NOT REPEAT THE RETRACTED CLAIM. `.planning/HANDOFF.json`
    `verified_this_session_firsthand[6]` RETRACTS "all 7 pinned files 0-line diff vs
    bf16289": `bf16289` was enforced by nothing and 5 of 8 files had drifted. Only
    `plink_ld_to_npz.py`, `condition_ld_matrix.py` and `occlusion_span_filter.py` are
    genuinely gated, and only since quick-260806-sr4. If the review states a freeze, it
    names the test that fails when it breaks, or writes "UNENFORCED — belief only".
    [[feedback_a_claimed_invariant_needs_a_named_enforcer]]
  * A green assertion is evidence only if you have seen it fail. Seven assertions in this
    arc were structurally incapable of failing.
    [[feedback_green_assertion_needs_a_negative_control]]
  * The suite run rewrites `tests/m3/sparse_parent_benchmark.tsv` (timing columns only).
    Restore it with `git checkout --` and confirm the tree is clean afterwards.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Collect the local evidence — one suite run, twenty checks, verbatim log + machine-readable TSV</name>
  <files>.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.log, .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.tsv</files>
  <read_first>
    - The `<interfaces>` block above, in full. Every command below is anchored there.
    - `.planning/HANDOFF.json` `suite_baselines`, `prep_landmines`, `data_state`.
  </read_first>
  <action>
    ⛔ NO PERIMETER CONTACT. No `gsutil`, `gcloud`, `bq`, `wb`. No cluster or VM action.
    ⛔ NO writes outside this quick directory (the one exception: `git checkout --` on
       `tests/m3/sparse_parent_benchmark.tsv`, which RESTORES rather than changes).

    **RUN THE ~14-MINUTE `tests/m3` SUITE EXACTLY ONCE**, here in this task. Tasks 2 and 3
    read this task's log and TSV; neither re-runs it. If you find yourself wanting to
    re-run it, you want to re-READ the log instead.

    **LOG FORMAT — mandatory, because Task 3's guard parses it.** Append one block per
    check to `260811-rcw-evidence.log`, in exactly this shape, with the command on a line
    beginning `$ ` and nothing else beginning `$ `:

        ##### L-01 | <one-line description>
        $ <the exact command run>
        <verbatim stdout+stderr, untrimmed for short outputs; for pytest, keep at minimum
         the final summary line and any F/E lines>
        --- exit: <rc>

    Run these twenty checks, in this order. Record OBSERVED verbatim — never the expected
    value restated. Verdict is `PASS` (observed == expected), `FAIL` (observed != expected
    in a way that bears on the fire), or `RED` (observed != expected on a check the project
    has ruled is not allowed to move, e.g. a skip count).

    | id | area | command | expected |
    |----|------|---------|----------|
    | L-01 | anchor | `git log -1 --date=iso --format='%H %ad'` | record; this is the review's "as of" commit + date |
    | L-02 | anchor | `git status --porcelain -- src tests config Snakefile` | EMPTY (no pre-existing source drift) |
    | L-03 | suite | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3 -q` | `902 passed, 31 skipped` / 0 failed. **Skips must be EXACTLY 31.** |
    | L-04 | suite | `... -m pytest tests/phase2 -q` | `136 passed, 1 skipped` / 0 failed. **Skips must be EXACTLY 1.** |
    | L-05 | DAG | `/rs1/.../smoke_dev/bin/snakemake --snakefile Snakefile m3_convert_aou_afr_rds_all -n --quiet` | exit 0, clean DAG, **575 jobs** |
    | L-06 | DAG | `/rs1/.../smoke_dev/bin/snakemake --snakefile Snakefile --list` | exit 0 (the MEDIUM-7 replacement for the struck full-workflow dry-run) |
    | L-07 | config | read `config/pipeline.yaml` with `yaml.safe_load`, print `ld_read_path` | `{enabled: True, ancestries: ['AFR'], allele_aware: True, coloc: True}` |
    | L-08 | config | same load, print the `strict_aou_only` value | `False` |
    | L-09 | config | same load, print `m3_convert_max_n_var` | `120000` |
    | L-10 | config | same load, print `allow_degraded` AND report whether `allow_partial_manifest` exists as a config key | `allow_degraded: False`; if `allow_partial_manifest` is ABSENT, record that plus its code default and the file:line it lives at (`src/python/assemble_occlusion_catalog.py`, the GATE 1 raise) |
    | L-11 | BLOCKER-1 | `grep -c -- '--ld-file {input.ld_matrix}' src/snakemake/rules/finemap.smk` | exactly `1` |
    | L-12 | BLOCKER-1 | `grep -cF 'region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],' src/snakemake/rules/finemap.smk` | exactly `1` (the guard rail is intact) |
    | L-13 | BLOCKER-1 | `... -m pytest tests/m3/test_ld_read_path.py -v` | all pass; **the four BEHAVIOURAL tests RAN, not skipped**. Record each behavioural test's PASSED/SKIPPED status individually. Any SKIP here is a RED. |
    | L-14 | BLOCKER-A | `... -m pytest tests/m3/test_ld_declared_authoritative.py -v` | all pass, **0 skipped** — this is the production-threshold suite |
    | L-15 | data | `test ! -e data/processed/ld_reference && echo ABSENT` | `ABSENT` (expected pre-fire) |
    | L-16 | data | `ls data/interim/aou_ld_exports/AFR_aou/*.npz 2>/dev/null \| wc -l` | `0` |
    | L-17 | manifest | with python: read `config/ld_regions.tsv` by HEADER NAME (never a positional column index), print the count of UNIQUE `region_id` and how many contain `__sub` | `276` unique, `123` with `__sub` |
    | L-18 | crosswalk | with python: read `config/curated_to_m2_region_map.tsv`, print the data-row count, the `m2_region_id`+`status` for `SH2B3_12q24`, and the `status` for `BMI_Xq24` | `12` data rows; SH2B3 -> `m2_region_00040__sub14` / `contained`; BMI_Xq24 -> `unmapped` |
    | L-19 | validation | `find .planning/phases/m3-aou-afr-ld-panel-build/validation -type f ! -name .gitkeep \| wc -l` | `0` — the pre-registered 4-check protocol has never been run |
    | L-20 | hygiene | `git checkout -- tests/m3/sparse_parent_benchmark.tsv 2>/dev/null; git status --porcelain -- src tests config Snakefile` | EMPTY. Proves the evidence run left zero source drift. |

    ⚠ ON L-03: if the passed count is NOT 902, do NOT quietly adopt the new number and do
    NOT call it a failure either. Record it, then RECONCILE it in the log against
    `git log --oneline b02707a..HEAD` — the intervening commits are the 260811-pmv docs
    arc and should add ZERO tests. A passed count that moved with only docs commits
    intervening is a FAIL that the review must surface loudly. The skip counts are the
    hard rule: 31 and 1, exactly.

    ⚠ ON L-03, THE COMPLETION RULE: if the `tests/m3` suite does not COMPLETE — it errors
    out, is killed, times out, hangs, or aborts at collection — that is a **RED**, recorded
    as such in the TSV. It is NOT a skip, NOT "inconclusive", and NOT an invitation to
    substitute a subset run as evidence. A subset run may be recorded as ADDITIONAL context
    under its own check id, but it never satisfies L-03. The verdict at §1 then takes the
    NOT-READY form, because the single largest body of agent-verifiable evidence is missing.

    ⚠ ON L-13: report the four behavioural tests by name. "8 passed" is not sufficient
    evidence — a suite that silently skipped its only behavioural assertions would also
    print a green line.

    **THEN write `260811-rcw-evidence.tsv`**, tab-separated, with this exact header:

        check_id	area	what	command	expected	observed	verdict	evidence_date

    One row per check. `command` and `observed` must be single-line-safe (replace embedded
    tabs/newlines with `; `). `evidence_date` is the date the command actually ran.
    Every row's `command` must appear verbatim on a `$ ` line in the log — Task 3 checks this.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate &amp;&amp; test -s 260811-rcw-evidence.log &amp;&amp; test -s 260811-rcw-evidence.tsv &amp;&amp; test "$(grep -c '^##### L-' 260811-rcw-evidence.log)" -eq 20 &amp;&amp; test "$(tail -n +2 260811-rcw-evidence.tsv | wc -l)" -eq 20 &amp;&amp; head -1 260811-rcw-evidence.tsv | grep -qP '^check_id\tarea\twhat\tcommand\texpected\tobserved\tverdict\tevidence_date$' &amp;&amp; test "$(grep -cE '^\$ .*(gsutil|gcloud|bq |wb )' 260811-rcw-evidence.log)" -eq 0 &amp;&amp; cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -z "$(git status --porcelain -- src tests config Snakefile)" &amp;&amp; echo EVIDENCE_OK</automated>
  </verify>
  <done>
    `260811-rcw-evidence.log` holds 20 `##### L-NN` blocks, each with a verbatim `$ ` command
    line, its real output and its exit code. `260811-rcw-evidence.tsv` holds a header plus 20
    rows, every `command` value matching a `$ ` line in the log. Zero perimeter commands were
    invoked (grep-proven over the log). `git status --porcelain -- src tests config Snakefile`
    is empty. The `tests/m3` suite ran exactly once.
  </done>
</task>

<task type="auto">
  <name>Task 2: Assemble the PRE-FIRE GATE REVIEW — reconciled gate table, perimeter gate-time checks, the Carter-only sequence, BLOCKS-vs-BOUNDS</name>
  <files>.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PRE-FIRE-GATE-REVIEW.md</files>
  <read_first>
    - `260811-rcw-evidence.tsv` and `260811-rcw-evidence.log` from Task 1. Every §3 number
      comes from here and nowhere else.
    - `m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md` **lines 1302-1536** (Task 3).
      Do not read the whole 1,650-line file.
    - `m3-04c-BLAST-RADIUS.md` §"Gate binding — what blocks what".
    - `.claude/skills/aou-ld-pipeline/SKILL.md` §"Wave 2 gate sequence" (lines 77-83).
    - `.planning/HANDOFF.json` — `gates`, `blast_radius_gate_ledger`, `cluster`,
      `data_state`, `do_not`, `carter_decisions_outstanding`, `inert_but_correct`.
    - `deferred-items.md` — the E-2 entry + its 2026-08-07 evidence update, E-4, K-2, K-3.
    - `260811-oku-SUMMARY.md` and `260811-pmv-SUMMARY.md` (state of the two open arcs only).
  </read_first>
  <action>
    ⛔ NO PERIMETER CONTACT. ⛔ Writes confined to this quick directory. Do NOT re-run the
    suite — read Task 1's log.

    Write `260811-rcw-PRE-FIRE-GATE-REVIEW.md` with these sections, in this order.

    **§0 — SCOPE STATEMENT (first thing on the page, before the verdict).** Verbatim intent:
    this document VERIFIES AND COLLATES; it fires nothing and authorizes nothing. Local
    evidence is a measurement taken on <date> at <commit L-01>. Perimeter state is
    LAST-KNOWN, not measured — no perimeter contact was made in producing this document.
    The fire decision and every gate-time action belong to Carter.

    **§1 — FIRE-READINESS VERDICT.** Exactly ONE line, in exactly one of these two forms —
    no third form, no hedging, no "mostly":

        **VERDICT:** All agent-verifiable preconditions GREEN as of <YYYY-MM-DD> at <commit>; every remaining item is Carter's gate-time check or Carter's decision.

        **VERDICT:** NOT READY — <N> RED(s): <one clause per RED, each naming its check_id>.

    Derive it mechanically: if every row of `260811-rcw-evidence.tsv` has verdict `PASS`,
    the first form; otherwise the second, listing every non-PASS row by `check_id`.
    Follow the verdict with a two-to-four-line "what this verdict does and does not mean"
    note: it covers the AGENT-VERIFIABLE preconditions only, and says nothing about the
    perimeter checks in §4 or the decisions in §5-§6.

    **§2 — CURRENT-STATE GATE TABLE.** ONE table reconciling all three records, columns:

        | Gate | Current status | Evidence (command or artifact + date) | What would change it |

    Rows — at minimum, and each traced to its winning record:
      * Panel reachability, Layer A (crosswalk) and Layer B (`--ld-file` read path)
      * BLOCKER-A — declared panel authoritative at production thresholds
      * BLOCKER-B — Track-A EUR numerics containment (`ld_read_path.ancestries`)
      * BLOCKER-C — something builds the `.rds` (`m3_convert_aou_afr_rds_all`)
      * BLOCKER-D — `.npz`->`.rds` converter sizing  ⚠ **PARTIAL**
      * The occlusion catalog refusal gates (`allow_degraded`, `allow_partial_manifest`)
      * Egress classification (skill GATE 0, RULED PASS 2026-04-28) — still live
      * CDR pin + cost/credit (skill GATE 1, CLEARED) and cohort rebuild (GATE 1.5, DONE)
      * The pre-registered 4-check validation protocol (never run; Check 2 redefined)
      * The stale `gs://` panel TSV, the manifest-egress gap, the real-`.bim` validation,
        the region-1 re-run — all four PERIMETER-ONLY, cross-referenced to §4
      * Suite + DAG health (L-03..L-06)

    Then a sub-section **§2.1 — DIVERGENCES BETWEEN THE RECORDS, STATED AND RESOLVED.**
    Cover, at minimum, the four divergences enumerated in `<interfaces>`: (1) HANDOFF's
    frozen narrative gate rows vs its own `blast_radius_gate_ledger`; (2) HANDOFF's
    `gates.m3_04c` 548P vs its own `suite_baselines` 902P; (3) the skill's Wave-2 table
    describing the KILLED Hail/A.3 producer — CR-01, the A.3 lowering hang, "322 cells",
    "44 egress bundles" are SUPERSEDED, **while its GATE 0 / GATE 1 / GATE 1.5 rows remain
    valid**; (4) the blast radius's fire row (A/C/D) vs HANDOFF's ledger (A/C closed, D
    partial). For each: name both records, both dates, the winner, and WHY (recency).
    Never present a merged status without showing the seam.

    **§3 — LOCAL RE-VERIFICATION (agent-verifiable, $0, NC-State).** A table rendering
    `260811-rcw-evidence.tsv`: check_id, what, command, expected, observed, verdict. Then:
      * a one-line statement of the skip-count rule and whether it held (31 and 1, exactly);
      * the L-13 behavioural-test roll-call BY NAME with each one's PASSED/SKIPPED state,
        plus the sentence that a skipped behavioural test would not be evidence;
      * the BLOCKER-1 acceptance-property paragraph: state the property from
        `DEC-2026-08-05-m3-ld-read-path` verbatim, name BOTH enforcing suites, and say
        plainly what each proves — `test_ld_read_path.py` pins `MIN_LD_OVERLAP <- 1L`
        because its loader-functions-only harness cuts above the real thresholds (:180-182),
        and `test_ld_declared_authoritative.py` is the production-threshold suite that
        READS `config/susie_policy.yaml`. Do not let a reader carry away the blast radius's
        "the gate is disabled in all 8 of them" as the current state;
      * the L-05/L-06 distinction: the targeted `m3_convert_aou_afr_rds_all` dry-run IS
        satisfiable and was run; the FULL-WORKFLOW `--dry-run` is STRUCK (D-04b-03 /
        MEDIUM-7) and `--list` is its substitute.
      * ⚠ ANY non-PASS row is rendered as a **loud RED block** immediately under the table
        — never as a footnote, never as a parenthetical.

    **§4 — WHAT CANNOT BE VERIFIED FROM HERE (perimeter-only).** A table:

        | Fact | Last known (+ date + source) | Carter's gate-time command (in-perimeter) | Expected result |

    Rows, at minimum:
      * Bucket `.npz` count — last known **0/276** (HANDOFF `data_state`, 2026-08-07).
        Command: `gsutil ls gs://<WORKSPACE_BUCKET>/ld/AFR_aou/*.npz | wc -l`. Expect 0
        pre-fire.
      * VM state — last known **STOPPED, not deleted**, `n1-standard-32`, holds
        `/home/jupyter/afr_cohort` (HANDOFF `cluster`, 2026-08-07). Read the AoU
        environment panel. ⚠ Carry the standing rule: **read the disk-type label before
        any destructive env action** — an AoU env on a STANDARD disk loses everything on
        delete; this project's rule is Reattachable persistent disk.
      * The stale `gs://` panel TSV (PRE-FIRE 2) — `gsutil stat <panel-uri>`; if present,
        `gsutil cat <uri> | head -1` must show **9 tab-separated columns**
        (`n_dropped_occluded` at `_PANEL_COLUMNS` index 7); otherwise `gsutil rm`.
        State WHY "0/276 banked" does not evidence the TSV's absence: the `.npz`, not the
        TSV, gates the resume skip, and prior fires appended `status=error` rows
        unconditionally.
      * The real-`.bim` validation (PRE-FIRE 3) — byte-check that the occlusion exclude
        list computed on the REAL cohort `.bim` is exactly the five expected region-1 ids
        at 1980475, 5733487, 5922718, 7492693, 8375822. ⚠ Carry the OPEN, UNRESOLVED
        0-vs-1-based index-origin question on
        `_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES` — an off-by-one validates the wrong rows.
      * Region-1 re-run result (STEP A) — cross-reference §5.

    Then, set apart and unmissable, **THE LIVENESS ARBITER FOR THE FIRE**: the GCS `.npz`
    object listing climbing to 276. **NOT the kernel light. NOT a `_SUCCESS` marker. NOT
    the log.** State the project's reason: `_SUCCESS` is written on driver-side task
    accounting, not contents validation.

    **§5 — THE CARTER-ONLY SEQUENCE.** Faithful to Task 3 (PLAN lines 1302-1536). Preserve
    its structure and its warnings; do not compress a warning into a clause:
      PRE-FIRE 1 (the occlusion manifest has no path out of the perimeter — what IS and is
        NOT recoverable, and the preferred per-region-file remedy);
      PRE-FIRE 1b (⚠ the `allow_degraded` DEAD-END — reproduce ALL THREE reachable
        branches (i)/(ii)/(iii) and the requirement to WRITE THE CHOSEN BRANCH DOWN BEFORE
        STEP B and RE-READ it at STEP E, because branch (ii) is only diagnosable after the
        fire; name both refusal gates and their line ranges);
      PRE-FIRE 2 (rotate the stale panel TSV); PRE-FIRE 3 (the gated real-`.bim` check);
      STEP A (region-1 re-run gate, INCLUDING the SH2B3 coverage check and its three
        honest remedies — all three flagged as scientific calls, not executor calls;
        and note the blast radius's correction that the core straddle is a NON-RISK
        because the panel is computed over the WINDOW, `overlap_frac` = 1.000000);
      STEP B (the fire: ~263 VM-h, ~11 days, **$385-1,084**, `nohup` + `timeout 312h`,
        check in every 2-3 days, do NOT restart the kernel, teardown is UI-only);
      STEP C (size and plan the egress; at most 22 chromosome groups plus size splits;
        confirm the REAL AoU threshold on the first request — 50 GB is OUR working
        ceiling, not AoU's documented cap);
      STEP D (egress per group + audit rows + SHA-256 sub-manifests + commit tokens);
      STEP E (hand back to the DAG under the branch recorded at PRE-FIRE 1b);
      STEP F (the OSF amendment-update for the Check-2 redefinition);
      STEP G (the end-to-end read-path proof on real data: `ld_file_declared == ld_matrix`,
        both an `AFR_aou/...rds` path, neither `identity` nor an `AFR/` path).

    Head the section with the cost band and, in its own block:
    **⛔ AN AGENT MUST NEVER FIRE THIS. It is Carter's terminal gate.**

    **§6 — OPEN ITEMS AT FIRE TIME.** A table with a column that is answered for EVERY row:

        | Item | State | BLOCKS THE FIRE? | What it BOUNDS | Where it lives |

    Be precise — most of these bound USAGE, not firing. Rows:
      * **BLOCKER-D (PARTIAL).** Does NOT block STEP B (the producer writes `.npz`; the OOM
        is on the CONSUMER). But it MATERIALLY BOUNDS the deliverable: only SH2B3
        `__sub14` is convertible, at 22.8 GB, on a big-memory node; MC4R (67.3 GB) and
        FTO/HLA (~553 GB) FAIL FAST at `m3_convert_max_n_var=120000` rather than OOM-killing.
        A sparse `.npz` is a PRODUCER-side change to a FROZEN file. Consequence, stated
        plainly: the fire banks `.npz` that cannot be converted for the large regions, so
        STEP E and the STEP G read-path proof are demonstrable only on the convertible
        subset. Say this at the top of the section — it is the one open item that changes
        what the money buys.
      * **The three E-2 disclosure obligations** — DECIDED as option A
        (`DEC-2026-08-07-e2-orientation-disposition`), obligations UNDISCHARGED: (1) the
        manuscript limitation paragraph naming `APOL1_22q12` **18.41%** and `FTO_16q12`
        **23.80%**; (2) the OSF record entry; (3) the OPEN framing question — LIMITATION or
        CORRECTION — which is above executor authority. Drafts exist at
        `.planning/quick/260811-oku-.../`. Does NOT block the fire; BOUNDS publication of
        any AFR coloc number. ⚠ Do NOT quote the 5.29% pooled figure alone.
      * **SR4-OPEN** — dossier at `.planning/quick/260811-pmv-.../`; the evidence supports
        NEVER-FROZEN for all five files; the disposition is Carter's and is OPEN. Does NOT
        block the fire; BOUNDS any claim that a file is "frozen".
      * **The OSF Check-2 amendment-update** — no redefined Check-2 result may be cited as
        PASSED until it is posted and its GUID recorded. Does NOT block the fire; BOUNDS
        citation. STEP F routes it.
      * **The pre-registered 4-check validation protocol** — never run (L-19). Does NOT
        block the fire; BOUNDS dev->production promotion and publication.
      * **K-2 (declined)** — state it correctly: the `ld_allele_join.R` extraction was
        DECLINED **on fire-path-risk grounds** (it would put a first-of-its-kind runtime
        `source()` dependency on the exact code path the ~11-day fire exercises). The
        decline PROTECTS the fire path. It is not an open risk against the fire.
      * **The identity-LD caveat** — every panel behind the E-2 numbers is an identity-LD
        stub (`use_identity` TRUE, `R` NULL, EUR/AFR/TRANS byte-identical). The numbers are
        the catalog<->panel-frame transposition rate and nothing more until a real panel
        exists. Does NOT block; BOUNDS how E-2's numbers may be cited.
      * **Findings E and G — INERT BUT CORRECT.** Cross-reference HANDOFF `inert_but_correct`:
        E is safe today only because ZERO AFR QTL-coloc jobs exist (E-4); G makes TRANS's
        failure VISIBLE, it does not make TRANS work. Neither may be cited as
        "production-exercised". Does NOT block; BOUNDS what may be claimed closed.

    **§7 — EVIDENCE INDEX.** Every artifact this review rests on, with its path and date:
    the two Task-1 files, the four layered records, the two decisions, the two sibling
    quick dirs. Plus one explicit line: **the claim "all 7 pinned files 0-line diff vs
    bf16289" is RETRACTED** and is not repeated anywhere in this review; the only three
    genuinely gated files are `plink_ld_to_npz.py`, `condition_ld_matrix.py` and
    `occlusion_span_filter.py`, gated by `tests/m3/test_source_freeze_pins.py`.

    ⚠ Every freeze or invariant this review asserts must NAME the test that fails when it
    breaks, or be written as "UNENFORCED — belief only". No exceptions.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate &amp;&amp; R=260811-rcw-PRE-FIRE-GATE-REVIEW.md &amp;&amp; test "$(wc -l &lt; $R)" -ge 180 &amp;&amp; test "$(grep -cE '^\*\*VERDICT:\*\* (All agent-verifiable preconditions GREEN|NOT READY)' $R)" -eq 1 &amp;&amp; for s in 'Scope' 'VERDICT' 'PRE-FIRE 1b' 'STEP G' 'BLOCKER-D' 'liveness' 'SR4-OPEN' 'bf16289'; do grep -qi -- "$s" $R || { echo "MISSING SECTION/TOKEN: $s"; exit 1; }; done &amp;&amp; grep -q '385' $R &amp;&amp; grep -qi 'NEVER FIRE' $R &amp;&amp; grep -q '0/276' $R &amp;&amp; grep -qi 'last known\|last-known' $R &amp;&amp; test "$(grep -cE 'L-(0[1-9]|1[0-9]|20)' $R)" -ge 15 &amp;&amp; cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -z "$(git status --porcelain -- src tests config Snakefile)" &amp;&amp; echo REVIEW_OK</automated>
  </verify>
  <done>
    `260811-rcw-PRE-FIRE-GATE-REVIEW.md` exists with all seven sections; carries exactly one
    verdict line in one of the two fixed forms; the gate table reconciles all three records
    with a §2.1 that names every divergence, both dates and the winner; §3 renders the
    evidence TSV with any non-PASS row as a loud RED block; §4 gives every perimeter fact as
    last-known + a gate-time command + expected result, and states the `.npz`-listing
    liveness arbiter; §5 reproduces the Carter-only sequence with the cost band and the
    never-an-agent rule; §6 answers BLOCKS-vs-BOUNDS for every open item; §7 indexes the
    evidence and records the bf16289 retraction. No source, test or config file changed.
  </done>
</task>

<task type="auto">
  <name>Task 3: Reconcile — re-derive every quoted number against the evidence, then commit</name>
  <files>.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PRE-FIRE-GATE-REVIEW.md, .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.tsv</files>
  <read_first>
    - `260811-rcw-PRE-FIRE-GATE-REVIEW.md` as written by Task 2.
    - `260811-rcw-evidence.tsv` and `260811-rcw-evidence.log` as written by Task 1.
  </read_first>
  <action>
    ⛔ NO PERIMETER CONTACT. ⛔ Do NOT re-run the `tests/m3` suite — reconcile against
    Task 1's log. ⛔ Writes confined to this quick directory.

    This task exists because this project has shipped a wrong number into a
    reader-facing document more than once, and because the last two reconciliation passes
    in this repo each found real defects. Assume this one will too.

    **STEP 1 — Enumerate every number and every proper-noun claim in the review.** Walk the
    document top to bottom and build a working list of: every numeric literal (counts,
    percentages, dollar figures, line numbers, commit SHAs, dates), every file path, every
    test name, and every gate status word. Do not skip §5 and §6 because they are prose —
    the 100x error this project made was inside a prose claim.

    **STEP 2 — Trace each one to a source.** Every item must resolve to exactly one of:
      (a) a row of `260811-rcw-evidence.tsv` (cite the `check_id`); or
      (b) a named in-repo record with a date (HANDOFF.json, the m3-04c PLAN, the blast
          radius, the skill, deferred-items.md, DECISIONS.md, a sibling quick SUMMARY); or
      (c) an arithmetic derivation from (a) or (b) that you re-perform NOW rather than
          copy.
    Anything that resolves to none of these is a defect: either source it or delete it.

    **STEP 3 — Re-perform every arithmetic claim.** Specifically re-check, by hand:
      * the local check counts and the pass/skip/fail arithmetic in §3 against the TSV;
      * every percentage carried from the E-2 record — a ratio is not a percent
        (this project shipped `0.2033` as "0.20%" when it is **20.33%**, a 100x error in
        the reassuring direction, inside the exact claim a decision was proposed on);
      * the region arithmetic: 276 unique region ids, 123 with `__sub`, 153 whole
        (153 + 123 = 276 — check it, do not assert it);
      * the BLOCKER-D sizes and which regions they bind;
      * the cost band and VM-hours.
    ⚠ Scope every count you re-derive. `grep -r` does NOT follow symlinks and `grep -R`
    from the repo root over-counts. If you re-count anything, say what tree you counted.

    **STEP 4 — Check the review against itself.** Two documents in this repo have shipped
    internally self-inconsistent numbers (a comment whose own cited totals did not
    subtract to its own figure). Verify that no two statements in the review contradict
    each other — in particular that §1's verdict is consistent with every row of §3, and
    that §2's gate statuses are consistent with §6's BLOCKS-vs-BOUNDS column.

    **STEP 5 — Check the guard rails.**
      * The verdict line matches the evidence: all-PASS ⇒ the GREEN form; otherwise the
        NOT-READY form listing every non-PASS `check_id`. If they disagree, the VERDICT is
        wrong, not the evidence.
      * Every asserted freeze/invariant names its enforcing test or says "UNENFORCED —
        belief only".
      * The retracted `bf16289` claim is not repeated as fact anywhere.
      * No divergence between records is presented as a merged status without its seam.
      * `grep -cE '^\$ .*(gsutil|gcloud|bq |wb )' 260811-rcw-evidence.log` is 0.

    **STEP 6 — Fix every defect found**, in the review and/or the TSV. Record each fix as a
    dated line in a new final section of the review, `## Reconciliation log (Task 3)`, in
    the form `- FIXED: <what was wrong> -> <what it now says> (source: <check_id or record>)`.
    If you find zero defects, write `- No defects found. <N> numeric claims and <M>
    proper-noun claims traced; <K> arithmetic claims re-performed.` — with real counts, not
    placeholders. A reconciliation section that says only "verified" is not evidence.

    **STEP 7 — Commit.** Explicit paths only; never `git add -A` or `git add .`:

        export PATH="$HOME/miniconda3/bin:$PATH"
        git add .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PLAN.md \
                .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.log \
                .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.tsv \
                .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PRE-FIRE-GATE-REVIEW.md
        git commit -m "docs(260811-rcw): m3-04c Task 3 PRE-FIRE GATE REVIEW -- verified and collated, fires nothing"

    Before committing, confirm `git status --porcelain -- src tests config Snakefile` is
    empty. If the GPFS object store throws "invalid object / Error building trees", apply
    the recovery recipe in `.planning/HANDOFF.json` `gpfs_object_store_recovery_recipe`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate &amp;&amp; R=260811-rcw-PRE-FIRE-GATE-REVIEW.md &amp;&amp; grep -q '## Reconciliation log (Task 3)' $R &amp;&amp; test "$(grep -cE '^\*\*VERDICT:\*\* (All agent-verifiable preconditions GREEN|NOT READY)' $R)" -eq 1 &amp;&amp; NONPASS=$(tail -n +2 260811-rcw-evidence.tsv | awk -F'\t' '$7!="PASS"' | wc -l) &amp;&amp; if [ "$NONPASS" -eq 0 ]; then grep -q '^\*\*VERDICT:\*\* All agent-verifiable preconditions GREEN' $R; else grep -q '^\*\*VERDICT:\*\* NOT READY' $R; fi &amp;&amp; test "$(grep -cE '^\$ .*(gsutil|gcloud|bq |wb )' 260811-rcw-evidence.log)" -eq 0 &amp;&amp; cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -z "$(git status --porcelain -- src tests config Snakefile)" &amp;&amp; git log -1 --format=%s | grep -q '260811-rcw' &amp;&amp; test -z "$(git status --porcelain -- .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate)" &amp;&amp; echo RECONCILED_AND_COMMITTED</automated>
  </verify>
  <done>
    Every numeric and proper-noun claim in the review traces to an evidence `check_id`, a
    dated in-repo record, or a re-performed derivation. The verdict line is mechanically
    consistent with the evidence TSV's verdict column. A `## Reconciliation log (Task 3)`
    section records each fix (or a real, counted no-defect statement). Zero perimeter
    commands appear in the evidence log. `src/`, `tests/`, `config/` and `Snakefile` are
    unchanged. All four quick-dir files are committed and the quick directory is clean.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Agent ↔ AoU VPC-SC perimeter | The hard boundary of this task. The agent is on the NC-State side and must not cross it in ANY direction, including read-only control-plane calls. Everything on the far side is last-known, not measured. |
| A claim in the review ↔ the command that produced it | The review is a decision surface for a ~$1,000 / 11-day spend. An unsourced number here is indistinguishable from a sourced one to the reader, and this project has shipped wrong numbers into reader-facing documents repeatedly. |
| Record recency ↔ merged status | Four records written on four dates, two mutually contradictory and one describing a killed producer. Silently merging them produces a status that no record actually supports. |
| A gate-time instruction ↔ an executed action | §4 and §5 contain real, runnable perimeter commands. They are INSTRUCTIONS FOR CARTER. The boundary between "documented" and "executed" is the entire point of this task. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-rcw-01 | Elevation of privilege | an agent firing the billed loop | mitigate | The prohibition is stated in `<absolute_constraints>`, repeated in all three task actions, and repeated in §5 of the deliverable. No task has a fire step, and no task's `verify` can pass by firing anything. |
| T-rcw-02 | Elevation of privilege | any perimeter contact at all | mitigate | `gsutil`/`gcloud`/`bq`/`wb` are forbidden outright. Enforced mechanically, not by promise: every command is logged with a `$ ` prefix and Tasks 1 and 3 both assert `grep -cE '^\$ .*(gsutil\|gcloud\|bq \|wb )' == 0` over the evidence log. Scoped to the LOG, not the review — the review legitimately contains those commands as text for Carter. |
| T-rcw-03 | Tampering | source/test/config drift from an evidence run | mitigate | `git status --porcelain -- src tests config Snakefile` is asserted EMPTY in all three tasks' automated verify. The single known-jitter file (`sparse_parent_benchmark.tsv`) is restored by `git checkout --`, which is the only permitted write outside the quick dir and is a restore, not a change. |
| T-rcw-04 | Spoofing | a green suite that silently skipped its evidence | mitigate | Skip counts are checked EXACTLY (31 and 1), not bounded; a moved skip count is a RED, not a pass. The four behavioural read-path tests are rolled call BY NAME with individual PASSED/SKIPPED state, because "8 passed" would also print green on a suite that skipped its only behavioural assertions. |
| T-rcw-05 | Repudiation | a number in the review with no producing command | mitigate | Task 1 records every command verbatim with its real output and exit code; Task 3 traces every numeric and proper-noun claim to a `check_id`, a dated record, or a re-performed derivation, and deletes or sources anything that resolves to none. |
| T-rcw-06 | Tampering | an arithmetic error in the reassuring direction | mitigate | Task 3 STEP 3 re-performs every arithmetic claim rather than copying it, with the 100x ratio-vs-percent error named explicitly as the precedent, and STEP 4 checks the document against itself for internal inconsistency. |
| T-rcw-07 | Information disclosure | presenting last-known perimeter state as current | mitigate | §4 is a separate section with a mandatory "Last known (+ date + source)" column, and §0 states up front that no perimeter contact was made. Task 2's verify greps for `last known` and `0/276`. |
| T-rcw-08 | Repudiation | repeating the retracted `bf16289` freeze claim | mitigate | The retraction is carried in `<interfaces>`, §7 records it explicitly, Task 2's verify greps for the `bf16289` token, and Task 3 STEP 5 checks it is not repeated as fact. Every asserted invariant must name its enforcing test or say "UNENFORCED — belief only". |
| T-rcw-09 | Denial of service | a hedged or absent verdict | mitigate | The verdict must match one of two fixed regexes, checked in Tasks 2 and 3, and Task 3 additionally asserts it is MECHANICALLY consistent with the evidence TSV's verdict column — all-PASS ⇒ GREEN form, else NOT-READY form. A hedged third form fails the check. |
| T-rcw-10 | Tampering | a stale placeholder shipping in the deliverable | mitigate | Task 2 derives the verdict itself rather than leaving a sentinel, and both Task 2 and Task 3 assert exactly one verdict line in a fixed form. Task 3's no-defect branch requires real counts, so a reconciliation section cannot pass by saying only "verified". |
| T-rcw-11 | Tampering | an executor touching a fake artifact to make a check pass | mitigate | Stated explicitly in `<interfaces>`: if any check tempts a `touch` of a fake `.rds` or an absent data directory, STOP and record it as a RED. L-15/L-16 EXPECT absence, so there is nothing to manufacture. |
| T-rcw-12 | Information disclosure | quoting the E-2 pooled 5.29% alone | mitigate | §6 carries the per-region numbers (`APOL1_22q12` 18.41%, `FTO_16q12` 23.80%) and the explicit standing instruction not to quote the pooled figure alone, plus the identity-LD-stub caveat that bounds all of them. |
| T-rcw-13 | Repudiation | a multi-terminal staging collision on GPFS | mitigate | Task 3 commits with explicit paths only; `git add -A` / `git add .` are forbidden in `<absolute_constraints>`. The GPFS object-store recovery recipe is referenced for the known loose-object failure. |
</threat_model>

<verification>
All checks are NC-State, `$0`, no perimeter.

1. `260811-rcw-evidence.log` holds exactly 20 `##### L-NN` blocks, each with a `$ ` command
   line, real output and an exit code.
2. `260811-rcw-evidence.tsv` holds the mandated header plus exactly 20 rows, and every row's
   `command` appears verbatim on a `$ ` line in the log.
3. `grep -cE '^\$ .*(gsutil|gcloud|bq |wb )' 260811-rcw-evidence.log` is `0` — zero perimeter
   contact, proven rather than promised.
4. `git status --porcelain -- src tests config Snakefile` is EMPTY after every task.
5. `260811-rcw-PRE-FIRE-GATE-REVIEW.md` has all seven sections and is ≥ 180 lines.
6. Exactly ONE verdict line, matching one of the two fixed forms, and mechanically
   consistent with the evidence TSV's verdict column.
7. §2.1 names every divergence with both records, both dates and the winner.
8. §4 gives every perimeter fact as last-known + date + source + gate-time command +
   expected result, and states the `.npz`-object-listing liveness arbiter with its two
   explicit negations (not the kernel light, not `_SUCCESS`).
9. §5 carries the cost band and the "AN AGENT MUST NEVER FIRE THIS" rule.
10. §6 answers BLOCKS-vs-BOUNDS for every open item, with BLOCKER-D's bounding of the
    deliverable stated at the top of the section.
11. `## Reconciliation log (Task 3)` exists with either dated fixes or a counted
    no-defect statement.
12. All four quick-dir files are committed; the quick directory is clean.
13. The `tests/m3` suite ran exactly ONCE across the whole plan.
</verification>

<success_criteria>
- Carter opens ONE file and can see, without cross-referencing four records himself, what
  is green, what is his to check in-perimeter, what is his to decide, and what the fire's
  outputs will and will not be usable for.
- Every local claim is traceable to a command whose real output sits in the same directory.
- Every perimeter claim is labelled last-known and comes with the command that refreshes it.
- The three layered records are reconciled with every seam visible and every winner named
  by recency — including the two places `.planning/HANDOFF.json` contradicts itself and the
  places the skill's Wave-2 table describes a producer that no longer exists.
- The verdict is one unhedged line, derived from the evidence rather than asserted.
- Nothing was fired, no cluster or VM was touched, no perimeter call of any kind was made,
  and no source, test or config file changed — all four checkable after the fact.
</success_criteria>

<output>
After completion, create
`.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-SUMMARY.md`
recording:
- The verdict line as shipped, and the evidence commit + date it is anchored to.
- The suite results as observed (passed / skipped / failed for both suites) and whether the
  31-and-1 skip rule held. If any count moved, the reconciliation against the intervening
  commits.
- Every non-PASS check by `check_id`, with what it means for the fire.
- The divergences found between the layered records, and how each was resolved.
- The reconciliation-log contents from Task 3: what was wrong and what it now says.
- An explicit statement that zero perimeter contact was made, that nothing was fired, and
  that `src/`, `tests/`, `config/` and `Snakefile` are unchanged — each with the check that
  proves it.
- What remains outstanding for Carter: the gate-time perimeter checks (§4), the PRE-FIRE
  decisions (§5), and the open items that bound usage (§6).
</output>
