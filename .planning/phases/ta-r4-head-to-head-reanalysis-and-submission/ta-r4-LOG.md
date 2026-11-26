# ta-r4 running log

Chronological record of every action in this phase. Append-only.

## 2026-10-21

- **Revival.** Carter: "There was a Track 1 publication that I started but didn't
  follow through with. I want to revive it and get it out for review." Then:
  "definitely run the re-analysis. Rigor over speed... use the gsd workflow, log
  everything, update Git." Track 1 = Track A = `docs/manuscript/id-vs-ref-LD.md`.
  The 2026-05-12 Genome Medicine package was never submitted.
- **Pre-phase review findings** (the reasons this phase exists):
  1. Headline claim ("identity-LD systematically inflates") is not a measurement:
     Results/Table 3 report 0 survived / 0 lost / 28 both-null; mean ΔPP.H4
     non-computable; identity-LD trait-pair comparator never run; SH2B3 survives.
  2. E-2 option A's rationale ("would move numbers in a manuscript under
     submission") is stale; transposed share 18.41% APOL1, 23.80% FTO.
  3. Table 3 lists SH2B3 canonical pairs "not executed"; Results reports PP.H4 = 1.0.
  4. Draft is ~16k words; 31 lines carry `.planning/` paths, commit hashes or DEC ids.
  5. m3-04c BLOCKER-B: EUR numbers move silently if `EUR_ukbb_pub` is built.
  6. OSF `osf-correction-v2` never posted (P-1 requires it by submission day).
- **Git repair (objects only; no tracked file changed).** `git fsck` showed 837
  broken links; `git log -- docs/manuscript/id-vs-ref-LD.md` failed with
  `unable to read tree`. Root cause found: `.git/objects/pack/pack-f4a99a73….idx`
  had NO `.pack` (a whole pack file lost on GPFS, not just loose objects).
  Repair: `git clone --mirror` of origin (== local HEAD `5c11293`) into the session
  scratchpad, `git repack -a -d`, copied `pack-3efade46….{pack,idx}` into
  `.git/objects/pack/`; orphan `.idx` moved to scratch backup (not deleted).
  Result: `fsck --connectivity-only` 0 broken/missing; every index blob present;
  manuscript history readable again.
- **Branch note.** CLAUDE.md asks for branch isolation, but this is a shared
  multi-terminal GPFS tree; switching branches would yank the working tree out
  from under any concurrent Track B session. Phase work is committed on the
  current branch (`m3-W2-aou-deltas`) with explicit-path staging only.
- Phase registered in ROADMAP.md (Track-A-R4 section) and STATE.md.
- **Fact found (scout):** all 28 empty R1 trait-pair rows are `status=no_signal`
  with `n_cs = 0` on at least one side (ta-r3 W2 SUMMARY) — coloc.susie never ran.
  Also: `coloc.abf` uses no LD matrix, so "identity LD" exists only inside SuSiE;
  the draft conflates them.
- **Inventory (background agent, read-only, banked verbatim as
  `ta-r4-INVENTORY-2026-10-21.md`):** every Track A fit (96 real + 95 identity),
  the 1000G EUR/AFR LD panels, variant lists, GTEx v8 QTL inputs and the QTL-coloc
  outputs are GONE — never git-tracked, purged from `/share` (30-day purge,
  inferred). Survivors: 8 harmonized sumstats (sha256 match), 1000G VCFs on /rs1,
  code/config, pinned `r_coloc` env, tracked aggregates. Hazards recorded:
  `02c4404` max_iter change, silent `diag(n)` fallback, AFR now routed to AoU
  paths, identity overlay depends on real panel, `envs/qtl_processing.yml`
  deleted but referenced, `coloc_summary.tsv` md5 ≠ the one the manuscript cites.
- **Discuss-phase decisions (Carter, two AskUserQuestion rounds):** three arms;
  coloc.abf fallback labelled separately; 1000G primary + UKB sensitivity in a
  separate path; OSF pre-registration posted before the production comparison;
  E-2 FIX then before/after (reverses DEC-2026-08-07 option A for Track A);
  exhaustive scope with AFR secondary; fresh draft; venue after results.
- **Orchestrator-locked (rigor rule):** regenerate everything; outputs on /rs1
  with committed sha256 manifests; known-answer reproduction (k2d identity n_CS,
  SH2B3 PP.H4=1.0 at max_iter=100) before production; named test against silent
  identity fallback; AFR/identity overlays; restore qtl_processing.yml; no Track B
  side effects.
- `ta-r4-CONTEXT.md` + `ta-r4-DISCUSSION-LOG.md` written.
- **Research complete** (`ta-r4-RESEARCH.md`, 688 lines, gsd-phase-researcher). Two of its
  corrections spot-checked by the orchestrator and CONFIRMED: (a) the SH2B3 PP.H4=1.0 came
  from L=15 lsweep fits swapped into the Stage-2 namespace (ta-sh2b3 W2 SUMMARY :153-156);
  (b) `config/regions_curated.csv` has **12** regions — the draft says "50 curated regions"
  (manuscript factual error to fix in the rewrite). Other key findings: E-2 reaches EUR
  fine-mapping (panel `.rds` has no REF/ALT; plink run without `--keep-allele-order`;
  BMI file lacks alleles); the naive QTL-side fix would orient the wrong object; p12 defaults
  differ between coloc.abf and coloc.susie; the legacy manifest admits only converged fits;
  negative controls cannot separate arms → simulation arm.
- **Carter decisions D-17..D-20** (SH2B3 exact-mix known answer; BMI allele restoration;
  fold osf-correction-v2 into the R4 amendment; AFR n=661). **Orchestrator-locked D-21..D-28.**
- **15:09 — Carter directive:** "continue with this analysis using --auto --chain choosing
  rigor over speed, but feel free to ask me any necessary questions." Interpretation applied:
  plan → check → execute without per-step confirmation; at every discretionary choice take the
  more rigorous option; STILL hard-stop for Carter at (a) the W4 OSF gate (D-27 sentinel — auto
  mode must never select past it), (b) any OSF posting or journal submission, (c) human-verify
  checkpoints whose outcome is a scientific judgement (panel manifest, known-answer findings,
  manuscript), (d) anything that spends AoU/cloud money (none planned).
- `ta-r4-VALIDATION.md` committed (`daedde5`).
- **Planning complete** (gsd-planner): 22 plans in 22 sequential waves + `ta-r4-PLAN-INDEX.md`
  (shared constants, standing rules, D-01..D-28 coverage). Planner-introduced rigor choices:
  analysis code frozen at a lock commit BEFORE the OSF post (W3c/W3d/W3e precede W4; W5–W6
  refuse to fire if analysis files differ from the lock); OSF sentinel must match the committed
  amendment sha256 AND the hash the public OSF API reports for the file on az52u; exhaustive
  36-case branch classifier; two brief-blind Codex reviews (amendment, manuscript); static
  246-row pair manifest (220 admissible) + static QTL manifest; manuscript numbers rendered only
  from FINAL tables; separate `Snakefile.ta_r4`; extra `A3_1kg_isect` arm (13 arms total).
  Corrections: legacy EUR panel count 10 (not 11); AFR 661 = 504 + ASW 61 + ACB 96 (measured).
  Committing plans before the plan-checker run.
- **Plan check iteration 1: ISSUES FOUND** (gsd-plan-checker): 7 blockers, 16 warnings, 6 info.
  Orchestrator VERIFIED B1 against `~/.claude/get-shit-done/workflows/execute-phase.md:636`:
  under auto/chain, `checkpoint:human-verify` is auto-approved with user_response "approved" and
  `checkpoint:decision` auto-selects the first option; ONLY `checkpoint:human-action` stops.
  So the LOG's promised scientific stops (item c, 15:09 entry) would NOT have held — corrected:
  every Carter-judgement checkpoint becomes `checkpoint:human-action` with a resume token the auto
  path cannot produce (`carter-approved YYYY-MM-DD`). Orchestrator fixed B7 (RESEARCH Open
  Questions marked RESOLVED → D-ids) and its own CONTEXT error (frozen file is
  `src/legacy/region_analysis/scripts/run_susie_rss.R`, not `src/snakemake/scripts/...`).
  Remaining blockers B1–B6 + all warnings sent to the planner (revision mode).
- **Plan revision iteration 1 complete** (gsd-planner): 25 plans / 25 sequential waves / 79 tasks,
  all with automated verify; VALIDATION `nyquist_compliant: true`. B1: every Carter checkpoint is
  `checkpoint:human-action`, resumable only by `carter-approved YYYY-MM-DD` + required keys, parsed
  by `src/python/ta_r4/signoff.py`, recorded verbatim in `signoffs/<ID>.yaml`, enforced by
  `test_signoffs.py`. B5: OSF API verified once per fire on the submit host → receipt bound to HEAD;
  in-job checks offline. New design element (planner, rigor rule — Carter can veto at the W4a
  lock): a THIRD negative-control set of 10 GWAS-null windows (P ≥ 1e-5 in all 8 Track A sumstats,
  seed 20261021), raising regions to 31 and the pair manifest to 346 rows / 320 admissible.
  New plan W2d applies Carter's W2c review choices (UKB HM3 restriction, QTL scope) before the lock.
- **Plan check iteration 2: 1 blocker, 5 warnings** (details + iteration-1 list banked in
  `ta-r4-PLAN-CHECK-LOG.md`). Orchestrator fixed the confirmatory row set (see that file) and
  sent all issues to the planner for revision 2 (final allowed iteration).
- **Plan revision 2 complete** (25 plans / 80 tasks): confirmatory set fixed in
  `config/ta_r4/decision_rules.yaml` (`confirmatory:` block) + `estimands.contrast_stats` +
  `run_aggregation.py` all pre-lock in W3d, rendered verbatim into the amendment; sign-off
  integrity text on all 8 human-action tasks; manifests keyed (ancestry, region_safe);
  `/data/r4` gitignored in W0a; R1_STRUCTURAL cause into the W3b findings + amendment (h).
- **Plan check iteration 3 (final): 0 blockers.** Two warnings + three info items applied by the
  orchestrator (see `ta-r4-PLAN-CHECK-LOG.md`). Planning closed; proceeding to
  `/gsd-execute-phase` under --auto --chain with human-action stops.

## 2026-10-21 — W0a executed (storage, survivors, env, baseline, DEC entries)

- **Tag:** `ta-r4-pre-baseline` (annotated, object `09e7795f`) → commit `3a2c1add`; pushed
  explicitly; `git ls-remote` shows `refs/tags/ta-r4-pre-baseline^{}` = `3a2c1add`. Created
  before any W0a commit so it marks the pre-R4 HEAD.
- **Storage:** `bin/r4_link_storage.sh` → `data/r4` -> `/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4`
  (2770 on root + 8 subdirs; group `oit-rs-researcher-ckclinto`, inherited from the parent).
  Second run: same realpath, exit 0. Refusal branch measured on a scratch fake repo: a real
  `data/r4` dir → exit 2, dir untouched. `/data/r4` appended to `.gitignore` (+1/-0).
- **Survivors:** N_SRC = 92 = 24 lsweep-backup files (6 dirs × 4) + 46 stage2_narrow_validation
  + 21 `coloc_susie_R2*` + 1 zip. Copied by `rsync -a --relative` to
  `data/r4/known_answer_survivors/`; sha256(copy) == sha256(source) for 92/92; sizes equal;
  manifest `manifests/survivors_sha256.tsv` 92 rows, 0 non-hex sha256. 19 of the 92 are `.rds`.
- **Env:** `envs/qtl_processing.yml` restored, `cmp` vs `c2dfb08^` IDENTICAL.
- **Conda cache isolation — plan premise FALSE (measured):** `CONDARC=$R4_CONDARC conda config
  --show pkgs_dirs` lists THREE dirs (shared `/rs1/.../conda_pkgs` included), because conda
  always reads `~/.condarc` and `~/.bashrc` exports `CONDA_PKGS_DIRS=/rs1/.../conda_pkgs`.
  Only `CONDA_PKGS_DIRS=$R4_CONDA_PREFIX/pkgs HOME=$R4_CONDA_PREFIX/home CONDARC=$R4_CONDARC`
  listed exactly one. That recipe also drops `~/.condarc`'s `channel_priority: strict` and
  `solver: libmamba`. Also measured: Snakemake 7.32.4 `--conda-cleanup-pkgs` defaults to None
  (cleans only when the flag is passed); the 2026-10-11 incident was Snakemake 9.x. Hand-off to
  W0b2 (`bin/r4_fire.sh`). `~/.condarc` NOT edited.
- **Baseline** (`tests/m3 tests/phase1 tests/phase2 -q -rA`, 16m10s): 1474 ids / 1428 passed /
  46 skipped / 0 failed (tests/m3 alone 1299 / 1265 / 34 / 0 = the 2026-09-19 record). Skipped
  ids = collected − PASSED ids; per-file skip counts equal the `-rA` SKIPPED [N] sums for all
  11 files. No pre-existing failure. Log: `data/r4/logs/tests_baseline_W0a.log`.
- **RED → GREEN:** `test_storage_on_rs1.py` 6 failed / 1 passed before the link, config and
  manifest existed; 7 passed after. Every negative control was also seen biting: each checker
  blinded → its test RED; a `/share/clintonlab` literal dropped into `config/ta_r4/` → RED.
- **DEC entries** appended (0 removed lines): `DEC-2026-10-21-ta-r4-e2-fix-supersedes-option-a`,
  `DEC-2026-10-21-osf-correction-v2-retired-unposted`, `DEC-2026-10-21-sh2b3-known-answer-premise`.
- **Wave close:** QUICK 7 passed (32 s cold first run, 0.4 s warm); HEAVY 0 selected (exit 5,
  no r4_heavy tests yet); `test_source_freeze_pins.py` 39 passed; FULL 1481 ids / 1435 passed /
  46 skipped / 0 failed (14m49s) = baseline 1474 + 7 new ta_r4; join vs baseline: 0 removed,
  7 added, 0 outcome changes. fsck before/after: 0 missing/broken.
- **Commits:** `c8130c5a` (T1), `c26d77ad` (T2), `6f968b1b` (T3 DEC), pushed.
- ⚠ **Hand-off to W0b1:** `tests/ta_r4/__init__.py` makes pytest import the test dir as the
  package `ta_r4` (`tests/` has no `__init__.py`), which shadows `src/python/ta_r4`. Measured
  on a scratch mock: `from ta_r4.paths import X` → `ModuleNotFoundError: No module named
  'ta_r4.paths'`. Without the `__init__.py`, `tests/ta_r4/conftest.py` becomes the bare
  `conftest` and breaks the tests/m3 `from conftest import R_SUBPROCESS_TIMEOUT_S` imports
  (also measured). W0b1 must pick a resolution before its first `from ta_r4...` test.
- **Orchestrator decisions after W0a (technical, not scientific):**
  (1) `ta_r4` import clash (tests/ta_r4 package shadows src/python/ta_r4): keep all plan paths;
  `tests/ta_r4/__init__.py` inserts `src/python` on sys.path then
  `__path__ = pkgutil.extend_path(__path__, __name__)`; W0b1 proves it with a test that
  `from ta_r4.paths import ...` imports and that `tests/m3` `from conftest import ...` still works.
  (2) conda isolation for W0b2's fire script = `CONDA_PKGS_DIRS=$R4_CONDA_PREFIX/pkgs
  HOME=$R4_CONDA_PREFIX/home CONDARC=$R4_CONDARC` (measured to list exactly one pkgs_dir), with
  `channel_priority: strict` and `solver: libmamba` written into the R4 condarc.
  Noted: /rs1 R4 dirs are group `oit-rs-researcher-ckclinto` (inherited), not `clintonlab`.

## 2026-10-21 — W0b1 executed (arms, paths, overlays, sign-off helper + sentinels)

- **Arms:** `src/python/ta_r4/arms.py` ARMS = 13 arms (8 production + 5 repro); stage is
  code-owned (`test_stage_is_code_not_config`). `paths.result_dirs("fits")` = 8 dirs (incl.
  A3_1kg_isect), `result_dirs("coloc")` = 10 (8 + A1_EUR + A1_AFR); no repro dir.
- **Overlays:** base + 13 arm overlays in `config/ta_r4/`; chain replaced wholesale + pinned;
  `config/pipeline.yaml`, Snakefile, all rules and the frozen script unchanged (`git diff --quiet` 0).
  Repro policy differs from `config/susie_policy.yaml` in one line (`max_iter_retry` 200 -> 100).
- **Import clash (orchestrator decision) fixed:** `tests/ta_r4/__init__.py` puts src/python first +
  `pkgutil.extend_path`; `test_import_isolation.py` RED without extend_path
  (`No module named 'ta_r4.arms'`), GREEN with it, incl. a tests/m3 `from conftest import` module
  in a subprocess, both orders.
- **Sign-off:** `ta_r4.signoff` rejects `approved` / `Approved.` / no date / bad date / future /
  pre-min / missing / empty / enum / unknown / duplicate keys (all `WAIT:`). Negative control: the
  plan's literal relaxed regex `^(carter-)?approved` turned 8 valid-reply tests RED but left the
  bare-approved rejections green (second layer: no date, missing key). A relaxation that also
  defaults the date turned 2 rejection tests RED. `test_signoffs.py`: every sentinel blinded →
  its fixture tests RED (4/4/1/1/1/1).
- **Hand-off to W2a/W2c:** sentinel reads Carter cells as `F` + `F_source == "Carter <date>"`;
  W2a's trait manifest needs a `type_source` column if `type` can be UNRESOLVED; review_decisions
  carries `trait_facts: {trait.<t>.<anc>.<field>: value}`. W4a: confirmatory_sha256 =
  `ta_r4.signoff.canonical_sha256(decision_rules["confirmatory"])`.
- **Wave close:** QUICK 91 passed, 8.3 s wall (7+2+25+35+22); HEAVY 0 selected; freeze pins 39
  passed; FULL 1565 ids / 1519 passed / 46 skipped / 0 failed (15m07s). Join vs
  tests_baseline_W0a.tsv: common 1474, removed 0, added 91 (all tests/ta_r4, passed), outcome
  changes 0; 1474 + 91 = 1565, 1428 + 91 = 1519.
- **Commits:** `714df7a5` (T1), `c6e9297f` (T2), docs commit follows; fsck clean before/after each.
- **Orchestrator spot-check of W0b1** (`47c9e9b`): origin HEAD matches; quick suite re-run by the
  orchestrator. Hand-offs carried forward: W2a must add a `type_source` column to the trait
  manifest if any trait `type` can be UNRESOLVED (W2c-T4 sign-off check reads `F_source`);
  `review_decisions.yaml` trait facts as `trait_facts: {trait.<t>.<anc>.<field>: value}`; W4a-T3
  prints `ta_r4.signoff.canonical_sha256(decision_rules["confirmatory"])` for Carter to sign.
- **18:39 — SESSION CLOSE requested (Carter relocating).** Terminal is not in tmux/screen, so the
  W0b2 executor would have died at an unknown point; the orchestrator stopped it via TaskStop
  after Task 2's commit (`ab77e97`) while Task 3 was mid conda-frontend solve. Verified: no
  conda/snakemake/pytest/bsub processes, `bjobs` empty, `data/r4/gate` absent. Task 3 WIP left
  uncommitted and inventoried (sha256 prefixes) in HANDOFF.json `ta_r4.in_progress`.
  Measured by W0b2 before the stop: compute node c017n03 has no route to api.osf.io (curl exit 28);
  login01 returns 200.

## 2026-10-22 — W0b2 resumed and closed (Task 3 finished, Task 4 wave-close)

- **Resume.** T1 `9bb65c01` and T2 `ab77e97c` were already committed. Their tests were re-run: T1 28 passed;
  T2 is inside the Task 3 run. The Task 3 WIP sha256 prefixes matched the hand-off. It was read line by line against
  the spec and conformed, except for the 3 fixes below. The stopped executor's T1/T2 RED evidence had never been
  written down; it was re-derived after the fact (modules moved aside → ImportError at collection; (o)-skip →
  `test_o_receipt_head_sha` DID NOT RAISE + `test_env_vars_do_not_change_pass`, 2 failed / 46 passed).
- **Task 3 RED → GREEN.** With the implementation moved to scratch: 9 failed / 55 passed / 3 errors. Restored on the
  unmodified WIP: 67 passed. Six more negative controls (gate call removed; CLI blinded; base config;
  crosswalk injection; forbidden path in a probe shell; ld_matrix_region_id name) all RED, each restored byte-identically.
- **Fixes to the WIP.** (1) The R4 condarc now has `channel_priority: flexible`. `envs/plink.yml` (bioconda first)
  is UNSATISFIABLE under strict with today's repodata (this is what stopped the previous solve; reproduced in
  scratch: strict rc=1, flexible rc=0). (2) The profile has `conda-frontend: conda` (Snakemake 7.32.4 defaults to mamba
  from condabin; isolation was measured for conda). (3) `bin/r4_fire.sh` runs `mkdir -p data/r4/logs/lsf`
  (bsub_wrapper only creates logs/lsf).
- **Env solve from scratch.** The stale `55c377a7…_.yaml`, `pkgs/`, `home/` and `condarc` were removed from the confirmed
  R4 prefix. `--conda-create-envs-only` rc=0 (10m08s). `--cores 1 --profile ''` was accepted (localrules), 4/4 steps.
  The three probe tools resolve inside the R4 env dirs. Lockfiles: plink 110 lines / qtl_processing 186 /
  python_stats 252 / r_coloc_named 224, each with `dependencies:`. Shared `/rs1/.../conda_pkgs`: archives 0 → 0,
  entries 2188 → 2188 (identical listing sha256), du 23348M → 23348M. R4 pkgs: 809 entries / 403 archives.
  `R4_PLINK=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin/plink`
  (PLINK v1.90b6.21).
- **Network probe (informational).** The LSF row was verified against `data/r4/logs/net_probe.404985.{out,err}` (c017n03,
  000, curl exit 28, 20004 ms timeout). The submit host was re-measured today: login03 → 200. The gate design does not depend on it.
- ⚠ **OSF anonymous-read finding (NOT fixed; for Carter / W4b).** `fetch_osf_file('k8w7n')` → HTTP 401.
  `curl` `/v2/files/k8w7n/`, `/v2/nodes/az52u/` and the redirect target `/v2/files/69ed77ef…/` → 401 "Authentication
  credentials were not provided". `/v2/registrations/pvb5j/` → 200, `public: True`. So the k8w7n known-answer
  dict could not be recorded. verify_online is anonymous by design, so it would fail closed (i) on any non-public
  node. W4b must confirm an anonymous API read returns 200 for the posted R4 file before the sentinel is written.
- **Measured.** Snakemake 7.32.4 prints the DAG-time OsfGateError on stdout (stderr empty). Tests assert on both streams.
- **Wave close.** QUICK 180 passed / 6 deselected, 24.9 s wall. HEAVY 6 passed (204 s). Freeze pins 39 passed.
  FULL 1660 ids / 1614 passed / 46 skipped / 0 failed (19m09s). Join vs tests_baseline_W0a.tsv (junit XML): common
  1474, removed 0, added 186 (all tests/ta_r4, passed), changed 0; tests/m3 1299/1299, 0 changed;
  1474 + 186 = 1660, 1428 + 186 = 1614. The main Snakefile / pipeline.yaml / frozen script / finemap.smk are unchanged.
  PLAN-INDEX §A now records the 10 NC_NULL tiles, the full conda-isolation recipe + flexible priority, and R4_PLINK.
  ARMS = 13 = §A (no change). Commits: `2d4da61e` (T3) + the wave-close commits; fsck clean before/after.

## 2026-10-22 — W0c executed (D-13 receipts, validator, r4_run_finemap, frozen-script e2e)

- **Task 1 RED → GREEN.** `test_no_silent_identity.py` written first: `55 failed in 2.20s`, all
  `ModuleNotFoundError: No module named 'ta_r4.validate_r4_fits'` / `No module named ta_r4.write_ld_receipt`.
  GREEN: `54 passed, 1 skipped` (skip = live gate, "no production fits yet (W5a enables)"). 24 injected silent shapes
  are each rejected by name (NULL-R identity/None, identity_fallback, ld_dir_missing as status and as ld_status,
  LD_DECLARED_ABSENT, matrix != declared, non-authoritative, non-allele-aware, md5 != manifest, LD fields missing,
  AFR receipt on an EUR fit, no row, no receipt, panel absent, receipt declared != fit, status not loaded, arm/mode
  mismatch, fallback_identity in ld_status; A2: points at the real panel, sha256 != manifest, NULL-R, declared not
  the arm's panel, identity_fallback).
  Negative controls: validator made to ignore `convergence_status` → `FAILED [a2_identity_fallback]`,
  `FAILED [identity_fallback]`, `2 failed, 52 passed`; receipt md5 check disabled → `FAILED test_receipt_writer_exits_3[md5_mismatch]`.
  Both restored (`cmp` identical). CLI on an identity fixture from src/python: 5 VIOLATION lines, `echo $?` → `1`.
- **Task 2 RED → GREEN.** e2e + variant-set tests written before `commands.py`/the rule: `3 failed, 1 passed, 1 skipped,
  6 errors` (ImportError `ta_r4.commands`; r4_run_finemap absent from `--list`; production dry-run raised no OsfGateError).
  GREEN with freeze pins: `49 passed, 1 skipped`; with the controls added later: e2e 9 + variant 4 (1 skip) + silent 56 (1 skip).
- **Fixture facts (60 SNPs, seed 20261021).** A3: `status ok`, `ld_matrix data/r4/ld/EUR_1kg_r4/FIX_1.rds` (== declared),
  `ld_status ld_loaded;overlap_ok;59;0.983`, `ld_allele_flipped 1`, `ld_allele_dropped_palindromic 1`, `ld_overlap 59`.
  A2: `ld_matrix data/r4/ld/EUR_identity_r4/FIX_1.rds`, same ld_status. Retained variants A3 59, A2 59, identical sets
  (60 − 1 palindrome = 59).
- **Missing-panel negative control (recorded verbatim):** the frozen script exited **rc 0** with
  `ld_matrix 'identity'`, `ld_status 'ld_dir_missing'`, `ld_file_declared 'data/r4/ld/EUR_1kg_r4/FIX_1.rds'`;
  validator violations `['LD_MATRIX_IDENTITY', 'LD_DIR_MISSING', 'LD_STATUS_NOT_LOADED', 'IDENTITY_SUBSTRING',
  'LD_MATRIX_NE_DECLARED']`; validator CLI rc 1. (In the rule, `test -s` and the receipt writer stop this case earlier.)
- **Rule-level runs (fixture repo from make_fixture_repo):** repro_routeC r4_run_finemap ran for real (receipt → frozen
  script → validator legacy_any `ld_source_class=real violations=0` → receipt one-liner `ld_fields_present`);
  the printed shell contains the three `shlex.join(commands.*)` strings. A3_1kg dry-run → OsfGateError `sentinel absent`.
  Manifest md5 swapped → job fails with `LD_RECEIPT_REFUSED ... != manifest md5`, frozen script never started, no JSON.
- **Task 2 sabotage controls (all RED, all restored `cmp` identical):** `--ld-file` dropped from fit_command →
  A3 fit rc 0 on `identity`/`ld_dir_missing`, 2 tests RED; receipt md5 check off → `test_rule_fails_on_panel_swap` RED;
  payload drops one variant → A2 58 vs A3 59, fixture set test RED; gate call removed from the input function →
  `test_rule_production_arm_refused_without_gate` RED. Live gates carry in-test controls (empty arm dir / identity fit;
  one arm of a pair alone / 58 vs 59 ids).
- **Measured:** the frozen loader also accepts a `Matrix::Diagonal` payload (rc 0, `ld_loaded;overlap_ok;59;0.983`);
  the builder keeps base `diag(n)`. The finemap.smk receipt one-liner is copied verbatim and produces identical output
  on the A3 JSON (test). `conda:` uses `workflow.basedir/envs/r_coloc.yml` (byte-identical to rules/envs/r_coloc.yml;
  plain `envs/r_coloc.yml` resolves rule-relative, which the fixture repo lacks — first rule run failed on it).
- **D-28:** `git diff --quiet HEAD -- run_susie_rss.R` → 0; `test_source_freeze_pins.py` 39 passed.
- **Wave close.** QUICK 235 passed / 20 deselected, 18.8 s wall. HEAVY 18 passed / 2 skipped (231 s). FULL
  1729 ids / 1681 passed / 48 skipped / 0 failed (19m28s). Join vs W0b2 junit (`full_W0b2.xml` → `full_W0c.xml`):
  common 1660, removed 0, changed 0, added 69 (silent 56, e2e 9, variant 4; 67 passed + 2 live-gate skips);
  1660 + 69 = 1729, 1614 + 67 = 1681, 46 + 2 = 48; tests/m3 1299/1299, 0 changed. sparse_parent_benchmark.tsv restored.
  Commits `dbc2c19d` (T1), `fef3589f` (T2), wave-close commit follows; fsck clean before.

## 2026-10-22 — W0d executed (run_coloc_pair_r4.R, r4_coloc_pair / r4_coloc_A1, toy --use-conda e2e)

- **Task 1 RED → GREEN.** test_coloc_pair_r4 / test_fallback_labelled / test_priors_constant written first, fixture
  fits built by the frozen script via `commands.fit_command`: `16 failed, 14 passed, 2 skipped`; every failure
  `Fatal error: cannot open file 'src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R'`. The 14 passes are the gate-checker
  unit tests (controlled below); the 2 skips are the live gates. GREEN: `30 passed, 2 skipped` (102.7 s).
- **Fixture numbers (verbatim test prints).** coloc_susie (FIXP_SAME) `pp_h4_max 0.999999999998337 direct
  0.999999999998337 max|diff| 0.0`. A1_matched (FIXP_MIX, n_snps 57) p12_primary `0.999441327677598`, direct coloc.abf
  with explicit priors identical (|diff| 0.0), package-default coloc.abf `0.999720585788306` (!=). Fallback (FIXP_NULL,
  n_cs_b 0): p12_primary fallback `0.0267819546730813` == A1_matched `0.0267819546730813`; p12_sensitivity
  `0.0521667809824499` == `0.0521667809824499`. A1 allvars n_snps 60 (59 allele-matched + 1 position-only) vs matched 57.
- **Sabotage REDs (each restored, `cmp` identical):** `P12 <- 1e-5` hard-coded → test_priors_constant `2 failed`
  (`test_every_mode_records_yaml_priors`, `test_explicit_prior_moves_the_answer`); fallback labelled `coloc_susie` →
  test_fallback_labelled `2 failed` (`assert ('coloc_susie' == 'fallback_abf'`); gate globbing every `results/*/coloc`
  → both repro-tree tests RED; n_cs check removed / p12 not compared / cross-arm check no-op → the matching checker
  test RED; UNMAPPED refusal disabled → override test RED.
- **Measured (name alignment).** The frozen script renames chr:pos sumstats SNP_IDs to LD-panel rsids
  ("Overriding 59 sumstats SNP_IDs with LD-panel rsids"). On that shape run_coloc_susie.R prints
  `fit_b=1/57 (intersect=0)`: it drops every non-CS column and colocalizes nothing. run_coloc_pair_r4.R stops with
  UNMAPPED_FIT_NAMES instead. On the rsid-vs-chr:pos shape both give `intersect=57`, same hits/nsnps/PPs.
  ⚠ DECISION NEEDED before W4 (analysis frozen at the OSF lock): W2a's 1000G panels carry .bim IDs (likely rsids),
  so production hypertension/stroke/t2d fits will have the override shape and refuse.
- **Measured (reader).** The named r_coloc env has no R.utils, so run_coloc_susie.R's `fread(<.bgz>)` fails and it
  silently skips its rewrite there. run_coloc_pair_r4.R uses the frozen script's reader (`fread(cmd = "gunzip -c ...")`).
- **Task 2.** Toy e2e RED (rule held aside): `4 failed, 1 passed` — `MissingRuleException: No rule to produce
  data/r4/results/A1_EUR/coloc/FIX_1__EUR__asthma_vs_bmi.matched.p12_primary.json`; the pass is the receipt negative
  control (fit rule only). That run was the first r_coloc solve into the R4 prefix: env `0f3436279d4146c376747a0ea5bfd4bf_`
  (R 4.4.2, coloc 5.2.3, susieR 0.14.2, R.utils 2.12.3). GREEN `5 passed`: A3_1kg 24 targets rc 0 in 50.3 s,
  A2_identity 12 targets rc 0 in 26.0 s. Negative control: FIX_2 A3 manifest row deleted → `Error in rule
  r4_run_finemap`, `LD_RECEIPT_REFUSED: no manifest row (EUR, FIX_2)`. Coloc gate refusal test (A1 allvars target, no
  sentinel) → OsfGateError; with the gate call removed → `MissingInputException in rule r4_coloc_A1` (RED), restored.
- **Shared conda cache** `/rs1/.../conda_pkgs`: before 2188 entries / listing sha256 `f094b37d…9085` / 23348 MB /
  0 archives; after all --use-conda runs identical, 0 entries newer than the start. R4 pkgs 809 → 1095 (546 archives).
- **Production dry-run (real repo).** Dirty tree: `REFUSED: uncommitted changes ... ?? src/snakemake/rules/ta_r4_coloc.smk`
  (rc 2). After commit: `OsfGateError: (a) sentinel absent` from verify-online (rc 1), Snakemake never started. Direct
  `$SMK -n`: `InputFunctionException in rule r4_coloc_pair ... OsfGateError: (a) sentinel absent` (and r4_coloc_A1).
  `bin/r4_fire.sh repro repro_routeC --list` lists r4_coloc_pair; r4_coloc_A1 is listed only under A3_1kg.
- **Wave close.** QUICK 254 passed / 39 deselected, 36.7 s wall. HEAVY 35 passed / 4 skipped (live gates), 7m14s.
  Freeze pins 39 passed. FULL 1767 ids / 1717 passed / 50 skipped / 0 failed (22m43s). Join vs `full_W0c.xml`:
  common 1729, removed 0, changed 0, added 38 (coloc_pair 11, fallback 11, priors 10, toy 6; 36 passed + 2 live-gate
  skips); 1729 + 38 = 1767, 1681 + 36 = 1717, 48 + 2 = 50; tests/m3 1299/1299, 0 changed. sparse_parent_benchmark.tsv
  restored. Frozen files (run_susie_rss.R, run_coloc_susie.R, Snakefile, pipeline.yaml, finemap.smk, envs/r_coloc.yml,
  Snakefile.ta_r4) 0-diff. Commits `99e05961` (T1), `c536547c` (T2), wave-close commit follows; fsck clean before.

## 2026-10-22 — W1 executed (E-2 orientation: BMI alleles, panel REF/ALT, QTL-beta orientation)

- **Unit 1 (D-18) RED → GREEN.** test_bmi_allele_restoration RED `5 failed, 5 errors` (`No module named
  ta_r4.restore_bmi_alleles`); GREEN `10 passed`. Controls (each restored, `cmp` identical): flipped class removed →
  class-count test RED (`{'exact': 2, ..._mismatch': 4}`) while `test_report_reconciles` stayed GREEN (the class test is
  the discriminating one); tolerance forced to 0 → 5 RED; sha256 check disabled → the 2 refusal tests RED.
- **Unit 1 real run** (`restore` 44 s): frozen bmi.EUR.tsv.bgz has **2,336,269** rows and the Yengo source
  **2,327,244** (the plan's interfaces block had the two counts swapped). Report: n_frozen 2336269 = exact 2327244 +
  flipped 0 + value_mismatch 0 + unjoined 9025 (awk: RECONCILED; equals `zcat | tail -n +2 | wc -l`). n_kept 2327244.
  n_sign_uninformative 23896 (all frozen BETA "0.0"; kept as exact). n_ambiguous_source 0 (9 frozen duplicate keys,
  byte-identical rows in both files). Raw cross-check (seed 20261021, 10000 kept rows): Tested_Allele == ALT
  10000/10000 (rate 1.000000). **FINDING:** the 9,025 unjoined rows are absent from the Yengo M1 file and are ALL A/T
  (3,844) or C/G (5,181) in the raw file, which has all 2,336,269 rows — they are dropped from R4, not restored.
  Output sha256 2f87e771…b1b4 (.bgz) / 36d01d38…572a (.tbi); index -s1 -b2 -e2 -S1 (frozen .tbi parameters).
  sumstats_r4_sha256.tsv 11 rows (9 inputs m1-verified + 2 outputs); `sha256sum -c` 11 OK.
- **Unit 2 RED → GREEN.** test_plink_ld_to_rds_ref_alt RED `8 failed, 3 passed` (`long flag "emit-ref-alt" is
  invalid`; the passes are the flag-absent identity and the plink property). GREEN `11 passed`, 0 skipped. Measured:
  `--keep-allele-order` R[1,2] 0.5000000000 == cor(A1 dosages) 0.5000000000; SNP 2 A1/A2 swapped with recoded dosage
  → -0.5000000000 == cor(d1, 2-d2); without `--keep-allele-order` → -0.5 (A1 major is re-coded). Sabotage
  `ALT = A2` → 2 RED (label assertions; a global label swap leaves every pairwise LD sign unchanged); per-SNP
  inconsistent ALT → known-answer correlation assertion RED; unconditional attr → 4 identity tests RED. My first swap
  test was wrong (kept the .bed, so A1 dosage was unchanged); fixed to recode the dosage as the plan says.
- **Unit 3 RED → GREEN.** test_qtl_orient RED `10 failed, 2 passed` (passes = flag-absent identity); GREEN 12 passed.
  `join$orient` sabotage → only `test_transposed_qtl_is_negated` RED (PP.H4 0.7488 vs 0.7178); `qtl_orient: FALSE`
  emitted off-flag → the 4 identity tests RED. Task verify (4 files) 141 passed.
- **Wave close.** QUICK 287 passed / 39 deselected, 112.2 s wall (budget 120 s; slowest = test_qtl_orient e2e ~11 s
  each). HEAVY 35 passed / 4 skipped (live gates), 6m59s. Freeze pins 39 passed. FULL 1800 ids / 1750 passed /
  50 skipped / 0 failed (24m01s, junit data/r4/logs/full_W1.xml). Join vs full_W0d.xml: common 1767, removed 0,
  changed 0, added 33 (bmi 10, plink 11, qtl_orient 12; all passed); 1767 + 33 = 1800, 1717 + 33 = 1750, 50 + 0 = 50;
  tests/m3 1299/1299, phase1 38/38, phase2 137/137, 0 changed (D-15). sparse_parent_benchmark.tsv restored. Shared
  conda cache after HEAVY: 2188 entries / f094b37d…9085 / 23348 MB / 0 archives (= W0d). Frozen files 0-diff.
  Commits `fb0a5b5c` (T1), `4896e011` (T2), `e7224a91` (T3), wave-close commit follows; fsck clean before.

## 2026-10-26 — W2a executed (EUR 1000G legacy + R4 panels, A2/k2d payloads, catalogs, trait manifest)

- **Task 1** (`f19d6398`, previous executor, 2026-10-23): Zenodo 10515792 tgz md5 `a7773ab485827b533cb300c76356d76b`, size
  288277344 (re-measured today); 66 members, single top dir; 22 `.fam` sha256 distinct = 1; **EUR n_samples = 489** (D-25;
  not 503). RED re-derived today (module aside → `1 error`), HTML-magic sabotage → `test_html_body_with_200_fails_magic` RED.
- **Resume.** Earlier fire: 130/136 then a killed resume fire; stale lock (5 W2a outputs, no live process/job) → unlocked via
  r4_fire.sh. All earlier W2a outputs DELETED and rebuilt; rebuild byte-identical (135/135 md5). Fire 1 hung at 124/136 on 7
  LSF jobs that exited before their script ran ("Cannot open your job file", c018n02/c014n04/c002n01; no .jobfailed marker)
  → stopped, re-fired, 12/12; final dry-run "Nothing to be done".
- **Counts.** EUR_1kg_r4 29, EUR_identity_r4 29, legacy_repro/EUR 10, k2d 24 (EUR 12 + AFR 12 = 24 distinct pairs in the k2d
  summary), catalogs 43 (legacy 12 + r4 31); 29+29+10+24+43 = 135 files. data/processed/ld_reference absent → 0 Track B writes.
- **SNP_ID format (pre-W4 decision input; nothing chosen).** Panels: R4 86,035/86,035 rsid, legacy 68,214/68,214 rsid, 0 chr:pos.
  Sumstats in the 10 admissible regions: hypertension/stroke/t2d EUR and stroke/t2d AFR 100% chr:pos; bmi 100% rsid; asthma
  EUR/AFR rsid or empty (32,491 / 23,471 empty). So hypertension/stroke/t2d fits will take the override shape.
- **Orientation.** A1 identical legacy vs R4 for all 68,214 variants (LDSC .bim A1 = minor): R4 == legacy matrices including sign.
- **Manifests** legacy 10 / R4 29 / identity 29 / k2d 24; max asym 0, max |diag-1| 0, finite; identity_exact 29/29; chmod a-w
  92 .rds. **Live gate** 8 passed, 0 skips; 181 checks = md5 92 + n_var 10 + |R| 10 + identity 29 + has_ref_alt 39 + sh2b3 1,
  all PASS, **0 FINDING rows**. **SH2B3 legacy n_var 895**; spectrum 210 neg / 81 < -1e-6 / rank 451 / cond 1.466e+07 = W1.5 audit.
  Fake-root controls: legacy→R4 swap → has_ref_alt FAIL; identity wrong region → identity FAIL; legacy wrong region →
  n_var + |R| FAIL; n_var 894 → FINDING (not FAIL). Unit sabotage (symmetry, duplicate, identity, md5) each RED.
- **Trait manifest** 8 rows. ⚠ **UNRESOLVED for W2c:** hypertension.EUR sdY. The file is Evangelou 2018 SBP (continuous, mmHg;
  sha256 = the sbp inventory entry), type quant; sdY.est median 10.72 (record only). BMI quant sdY 1 (inverse-rank-normal;
  sdY.est 1.012). asthma/stroke/t2d cc. stroke.EUR = METASTROKE N 75000 constant; stroke.AFR / stroke.EUR sha256 ≠ GIGASTROKE
  inventory entries; t2d.AFR N = Neff.
- **Wave close.** QUICK 304 passed in 125.7 s (> 120 s) → 5 test_qtl_orient e2e marked r4_heavy → 299 passed / 46 deselected,
  73.1 s. HEAVY 42 passed / 4 skipped (10m39s). Pins 39 passed. FULL 1819 ids / 1769 passed / 50 skipped / 0 failed
  (27m49s, `full_W2a.xml`). Join vs full_W1.xml: common 1800, removed 0, changed 0, added 19 (fetch 11, panels 8; passed);
  1800+19 = 1819, 1750+19 = 1769; tests/m3 1299/1299, phase1 38, phase2 137, 0 changed. sparse_parent_benchmark.tsv restored.
  Shared conda cache 2188 / f094b37d…9085 / 0 archives before and after (23348 MB before; 0 entries newer). Frozen files 0-diff.
  Commits `8a5c75e2` (T2), `b266e1d8` (T3), wave-close commit follows; fsck clean before/after each.

## 2026-10-27 — W2b executed (AFR 661/504 panels, legacy AFR repro, UKB 337k loader + native/isect panels)

- **Resume.** The stopped session's WIP was verified by content, not presence. Restored 2 purged forensics logs (not committed).
- **Task 1** (`37a391e4`): AFR504 = AFR.samples (sha256 97ff9e57…); AFR661 = 504 + ASW 61 + ACB 96 (157, 0 overlap); .fam IIDs ==
  sample lists. 20 R4 panels: n_var == .bim, REF/ALT == .bim A2/A1, asym 0, |diag-1| 0. 10 AFR661 identity payloads identical()
  frames. Legacy AFR 12 (= frozen 36 AFR fits / 3 traits; TRACK-A-FROZEN-NUMBERS.md:64 + IDENTITY-LD-K2D-FIT-SUMMARY.tsv), **12/12
  use_identity placeholders**. FINDING afr_panel_size.tsv: BMI_5q13_3 21323/21154 and PYHIN1 20818/20686 > 16000.
- **Task 2** (`f6d637aa`): RED re-derived (module absent → collection error; 8 sabotages each RED; the two diagonal guards mask
  each other, both off → 3 RED). Live tile chr12_111000001_114000001: diag == 1 exactly, symmetric; sign agreement 21409/21410 =
  0.999953 (745 shared, 717 flipped). No-D.R.D control still passed at 0.992760 overall → mixed-orientation assertion added:
  154/154 = 1.0, control 0/154 RED. Halving control → 3 RED.
- **Task 3** (`fa91305f`, fixes `0e621884`, `1d900305`): 121 candidate tiles HEADed; 7 chr6 26-35 Mb .npz are 404 → HLA native has
  a 28-33 Mb hole. 41 files fetched; tile manifest 76 rows (39 gz + 37 npz), size/ETag == HEAD, sha256 == disk. Native 30, isect
  29, 1000G isect 29; isect frames identical() 29/29; isect sign agreement min 0.990293 (APOL1), mixed min 0.999347. Native > 16000:
  HLA 34361, PYHIN1 26050, BMI_5q13_3 24121, SLC2A9 16752. Isect 71,769 of 86,035 EUR_1kg_r4 variants (palindromes dropped).
  Fires: LSF exit-255 losses stalled #1, #2 and #4 (#4 at 52/60: 7 jobs lost) → stopped, unlocked (UKB-only lock), re-fired. UKB
  rebuilt from scratch twice (declared code input changed); all builds byte-identical (122/122, 147/147). UKB jobs ran in the
  r_coloc job env (0f343627…, yaml == envs/r_coloc.yml, R 4.4.2).
- **Wave close.** QUICK 330 passed / 50 deselected, 74.6 s (one load-affected run 144.5 s). HEAVY 46 passed / 4 skipped (14m26s).
  Pins 39 passed. FULL 1854 ids / 1804 passed / 50 skipped / 0 failed (29m54s, full_W2b.xml). Vs full_W2a.xml: common 1819,
  removed 0, changed 0, added 35 (loader 30, triangle 4, fetch 1); tests/m3 1299 (1265/34) unchanged, phase1 38, phase2 137.
  Shared conda cache 2188 / f094b37d… / 0 archives before and after. Frozen files 0-diff. fsck clean before/after each commit.

## 2026-10-28 — W2c Tasks 1–3 executed (GTEx QTL downloads, static QTL manifest, W2 review packet); STOPPED at Task 4

- **Task 1** (`e3afa4dd`). Downloader PID 1793323 `FINISHED todo=98 failed=0`; `RESOLVED_COUNT 98 = 49 tissues x 2 sources`;
  `HEAD_OK 98 total_bytes 192123270766`. Verify awk → `98 0`. sum(size) + sum(tbi) = `191965693189 + 157577577 = 192123270766`
  = HEAD_OK total. `du -sh data/r4/downloads/eqtl_catalogue` → `180G`; 98 QTD dirs + empty `_tbi_stage`; `find data/raw -newer
  fetch_eqtl_catalogue.py` → nothing. Published checksums: the QTD000116, QTD000121, QTS000015 and sumstats/ listings have no md5
  file (checked 2026-10-28) → all 98 rows `no published checksum`.
- **Task 2 RED.** First recorded in `33d5f640` (`6 failed, 8 errors`, ImportError) and its controls in `14318720`. Re-derived
  today (pyc deleted, PYTHONDONTWRITEBYTECODE=1, cmp-restored): module moved aside → `6 failed, 8 errors in 1.06s`; check_schema
  no-op → `FAILED test_schema_rejects_status_or_tier_column`; `"tier"` appended to COLUMNS → `FAILED
  test_schema_rejects_status_or_tier_column`, `FAILED test_written_manifest_deterministic`. Committed-manifest controls:
  `tier` column appended to the TSV → `Left contains one more item: 'tier'` (RED); stroke rows dropped → `assert 93240 ==
  (23310 * 5)` (RED); restored sha256 0f10d922…4ad8.
- **Task 2 build** (LSF 429971–429975, 429980 after `Cannot open your job file` on 429975). `review_decisions.yaml` absent →
  `full`. `scope=full frozen_tissues=49 (src/python/build_tissue_n_lookup.py:25 GTEX_V8_TISSUE_N_FALLBACK) files=98 regions=10
  traits=5 features=23310 rows=116550`, 205 s. full_a == full_b == committed sha256 `0f10d9223833…4ad8`; tissues_frozen
  identical to full; eqtl_only == tf+eo `fce5f86b…5c85` (105745 rows, 21149 features). **Reconciliation:** `awk 'NR>1' | wc -l`
  = **116550** = 5 × **23310** unique (region, source, tissue, feature); dropping qtl_row_id+trait also gives 23310. Per source:
  eqtl 105745 + sqtl 10805 = 116550. Per region (rows/features): 9p21 4055/811, APOE 30930/6186, APOL1 10070/2014, BMI_5q13_3
  12195/2439, CXADR_F2RL1 5855/1171, FTO 4905/981, MC4R 5465/1093, PYHIN1 27125/5425, SH2B3 9740/1948, SLC2A9 6210/1242; sum of
  features 23310. Per trait 23310 × 5. Groups (region, source, qtd) 899 = eqtl 490 + sqtl 409.
- **Frozen QTL layer re-derived.** Legacy `build_manifest` with gtex_eqtl+gtex_sqtl and the 49-tissue fallback → **1274** rows
  (= TRACK-A-FROZEN-NUMBERS.md 1274): 10 regions (HLA_6p21 in, BMI_5q13.3 out), EUR, 4 traits (first per region), 13 curated
  genes. R4 coverage: 412 / 1274 (eqtl 379, sqtl 33). Missing 862 = HLA 98 + SLC2A9 ENSG00000109107 98 + CXADR 98 + F2RL1 98
  + MC4R 98 + 372 (sqtl 359, eqtl 13 where the gene lacks rows in that tissue). **FINDING** for Task 4 (packet §7).
- **t_row.** No legacy QTL logs survive (`find results data/r4/known_answer_survivors -path '*qtl*' -name '*.log'` → 0). Fixture
  timing LSF 429976 (tests/phase2 has no runnable fixture; used the test_qtl_orient 200-variant fixture): `N 15 median_s 2.397
  min 2.290 max 7.224 median_json_bytes 1355`. Labelled "fixture lower bound, UNMEASURED on real data". Estimate (rows × 3 ×
  t_row): full 116550 rows / 899 groups / 232.8 core-h / 0.474 GB; tissues_frozen same; eqtl_only and tf+eo 105745 / 490 /
  211.2 / 0.430.
- **Deviation.** My first verify ran the r4_heavy determinism test on login01 for ~2.5 min (2 builds); killed. The file was
  intact (sha256 0f10d922…). All later heavy runs went on LSF.
- **Open-item evidence (packet §4).** stroke.AFR: local GCST90104553 md5 `c63fdaba…fee4` = published; meta.yaml trait "Small
  vessel stroke" (EFO_1001504), sample_size 20453. GCST90104549 = "Stroke" (EFO_0000712), 23991, md5 `15d6213c…` = published,
  sha256 `220d2610…` = inventory sha256_raw. stroke.AFR.tsv.bgz (sha256 bf08ef28…) vs GCST90104553: `raw_rows 5259724 r4_rows
  5259724 joined_ALT=effect_allele 5259724 joined_flipped 0 unjoined 0`; BETA/SE/P/EAF equal 5259724; N {20271} (LSF 429983).
  Inventory harmonized all-stroke file sha256 `3c58b250…` = inventory sha256_harmonized (LSF 429984). hypertension sdY: Evangelou
  2018 Supp. Table 1a SBP SD 20.7 mmHg (UKB+BiLEVE N 458,575), fetched to `data/r4/downloads/evangelou2018_supp/` (sha256
  a24bdb44…; row added to downloads_sha256.tsv; md5 computed, none published); sdY.est median 10.72 (trait_facts.tsv).
- **Wave close (LSF 429989, c018n02).** VERIFY test_qtl_manifest.py `14 passed` (7m54s, incl. r4_heavy). QUICK `343 passed, 51
  deselected`, 96.0 s. HEAVY `47 passed, 4 skipped` (21m22s; the 4 = W5a/W5b-enabled skips). Pins `39 passed`. FULL `1818
  passed, 50 skipped` (39m58s, full_W2c.xml). Vs full_W2b.xml: common 1854, removed 0, changed 0, added 14 (test_qtl_manifest,
  all passed); 1854 + 14 = 1868 ids, 1804 + 14 = 1818, 50 + 0 = 50; tests/m3 1299 (1265/34) unchanged. sparse_parent_benchmark.tsv
  restored. Shared conda cache 2188 / f094b37d… / 0 archives before and after, 0 entries newer. Frozen files 0-diff since
  1a887069. Commits `e3afa4dd` (T1), `f288ab82` (T2), packet + wave-close commit follows.
- **STOP at Task 4.** No sign-off recorded. Carter's 2026-10-27 "carter approved 10-27-2026 / proceed with your recommendations"
  predates the packet and does not match `carter-approved YYYY-MM-DD`; it is not a sign-off.
- **Pushed.** Wave-close commit `57da00e6`; `git push origin HEAD` → `14318720..57da00e6  HEAD -> m3-W2-aou-deltas`; fsck clean before/after.

## 2026-10-28 — W2c Task 4: Carter sign-off recorded

Two earlier replies were WAIT and recorded nothing: `carter-approved 10-28-2026` (signoff rc=1, wrong date format) and a reply with the `<...>` placeholders unfilled (not run). Carter's reply, verbatim:

```
carter-approved 2026-10-28
ukb_native: native
qtl_scope: full
trait.hypertension.EUR.sdY: 20.7
```

- `ta_r4.signoff record W2c-T4 --min-date 2026-10-28 --extra-required trait.hypertension.EUR.sdY` → rc 0, `signoffs/W2c-T4.yaml`, raw_sha256 `26e3c3020026af8616c5751f9fcacf11988aefeb4f932d693e973b7b8bfa2f3c`.
- `config/ta_r4/review_decisions.yaml` written from the recorded `fields` only; `trait_manifest.tsv` hypertension.EUR sdY = 20.7, sdY_source = `Carter 2026-10-28`; 0 UNRESOLVED cells remain.
- sdY 20.7 = Evangelou 2018 Supp. Table 1a UKB+BiLEVE SBP SD (packet §4); coloc `sdY.est` median 10.72 is the recorded caveat.
- stroke.AFR (§4b, GCST90104553 small vessel stroke): Carter raised no change; the packet had no reply key for it.

## 2026-10-28 — quick-261028-kkg: production gate = git lock (DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf)

- **Commits.** `26b358e2` feat: `ta_r4.r4_lock_gate` + W4b-T3 schema `lock_sha: <40-hex>` (+ `check_lock_record` in
  test_signoffs, `write_fixture_lock`). `b119c34e` refactor: Snakefile/rules/`bin/r4_fire.sh` use the lock gate;
  `r4_osf_gate.py` and `test_osf_gate.py` deleted.
- **RED.** Before the module existed: `ImportError: cannot import name 'r4_lock_gate' from 'ta_r4'` (collection error);
  test_signoff `2 failed, 36 passed` (`posted: yes` still accepted; valid `lock_sha` reply rejected).
- **Negative control (unit).** Checks (g)/(h) blinded to `pass`: `-k drift` → `3 failed, 1 passed` (the 1 is the
  outside-LOCKED_PATHS edit, which must pass). Restored, `cmp` identical, `__pycache__` cleared → `4 passed`.
- **Negative control (end to end).** Fixture repo, after `write_fixture_lock`: production `r4_gate_probe` dry-run rc 0;
  an uncommitted edit to `src/python/ta_r4/arms.py` → refused, `LockGateError ... drifted`. In the toy e2e, the
  uncommitted manifest-row deletion is now refused by the lock gate first; re-locked, it reaches `LD_RECEIPT_REFUSED`.
- **Reconciliation by id (tests/ta_r4, quick + heavy, LSF 430489 before / 430615 after).** Before 390 passed + 4 skipped.
  Removed 55 = 52 test_osf_gate + 3 replaced (`test_other_enum_violations[W4b-T3 ... posted: no]`,
  `test_real_repo[check_osf_sentinel]`, `test_tracked_osf_sentinel_requires_w4b`). Added 51 = 45 test_lock_gate +
  4 test_signoff + 2 test_signoffs. 390 − 55 + 51 = 386 passed; 4 skipped (same 4 W5a/W5b reasons); 0 changed.
- **FULL** `1814 passed, 50 skipped` (0 failed; 37m27s) = 1864 ids. Vs full_W2c.xml (1868/1818/50): the same −55/+51,
  0 changed. Pins `39 passed`. sparse_parent_benchmark.tsv restored. run_susie_rss.R 0-diff.
- **Real repo.** `bash bin/r4_fire.sh production A3_1kg -n r4_gate_probe` → `LockGateError: (a) lock record absent:
  .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json`, rc 1.
  `bash bin/r4_fire.sh repro repro_routeC -n r4_gate_probe_repro` → dry-run lists the probe, rc 0.
- Records: DEC appended; osf_deviations R4 entry; PLAN-INDEX, CONTEXT (D-05/D-27 superseded lines), VALIDATION and the
  pending W3d/W3e/W4a/W4b/W5a/W5b/W5c/W6/W7 plans now gate on the lock; OSF posting is optional.

## 2026-10-28 — W2d executed (apply W2c-T4 decisions)

- Preconditions: `coloc_priors.yaml` locked: false; `decision_rules.yaml` / `simulation.yaml` not yet created; no R4-LOCK.json.
  `signoff verify W2c-T4` rc 0 → `{"qtl_scope": "full", "trait.hypertension.EUR.sdY": "20.7", "ukb_native": "native"}`.
- W2d: ukb_native=native (Carter 2026-10-28), no-op. ARMS['A3_ukb'].panel_dir = EUR_ukb337k_r4; arms.py and
  overlay_A3_ukb.yaml 0-diff vs HEAD; overlay/isolation/signoffs tests `62 passed`.
- W2d: qtl_scope=full (Carter 2026-10-28), no-op. qtl_manifest.tsv 0-diff vs HEAD; 116550 rows = qtl_compute_estimate
  `full` n_rows 116550; test_qtl_manifest.py `14 passed` (5m10s).
- Wave close (LSF 431166, c018n03, HEAD d222f160). QUICK `339 passed, 51 deselected` (107 s). HEAVY `47 passed, 4 skipped`
  (19m25s; same 4 W5a/W5b skips). Pins `39 passed`. FULL `1814 passed, 50 skipped` (36m26s, full_W2d.xml) = 1864 ids. Vs
  full_W2c.xml: common 1813, removed 55 / added 51 (the kkg osf→lock-gate swap), changed 0; tests/m3 1299 (1265/34) unchanged.
  sparse_parent_benchmark.tsv restored. Commits `99329eca` (T1), `d222f160` (T2), wave-close commit follows.

## 2026-10-29 — W3a executed (known-answer routes)

- **Route L code.** `bin/r4_extract_legacy_code.sh 3dd76df`: run_susie_rss.R sources no repo file (library() only), so
  1 file + the convenience copy; sha256 62fbe9da… (legacy_code_sha256.tsv, 2 rows). Blob 75f2d34 = git object, and the
  same blob at 0948a76, 1635d37 and 08beb4c: the alternates are byte-identical and were not run.
  `config/susie_policy.yaml` is 0-diff vs 3dd76df. Commit `49a8f47b`.
- **Fires** (`data/r4/results/<arm>/fine_mapping/susie`, /rs1). routeC 96, routeL 96, k2d_routeC 95, k2d_routeL 95 = 382;
  dry-run "Nothing to be done" for each. fits_repro_sha256.tsv 764 rows = 2 × 382. k2d omits bmi.EUR.APOE_19q13
  (absent from the k2d manifest input; TRACK-A-FROZEN-NUMBERS.md:26). Receipts: real-LD 86 legacy_panel + 10 missing
  (EUR HLA_6p21 + BMI_Xq24 × 5 traits) = 96; k2d 95 legacy_panel. 15 jobs died at LSF start with exit 255
  (C 7, L 4, k2dC 1, k2dL 3); a watchdog killed the waiting Snakemake, unlocked and re-fired. No R errors. Commit `741f44b5`.
- **Route C vs Route L** (known_answer_W3a.tsv, 191 rows = 96 + 95). Equal 96 + differ 0 = 96 (real-LD); equal 95 +
  differ 0 = 95 (k2d). max |ΔPIP| = 0 on 131 fits with a PIP vector (66 + 65); 60 early exits (30 + 30) have none.
  No code drift is detected under the reproduction semantics.
- **vs k2d record** (both routes identical). status 95 + 0 = 95; n_CS 95 + 0 = 95; cs_sizes 47 + 48 = 95.
  FINDING: the 48 cs_sizes differences are all the non-empty fits. The record's cs_sizes column equals
  `len("CS<i>")` for i = 1..n_CS on 95/95 rows (e.g. 10 sets → `3;…;3;4`): the summariser iterated CS keys. Aggregates
  65 ok / 24 too_many_variants / 6 no_variants and non-empty 48/95 equal the record.
- **vs frozen real-LD** (both routes identical). non-empty 51/96 = 51. Status 44 ok + 22 non_converged + 24
  too_many_variants + 6 no_variants = 96, vs frozen 48 + 18 + 24 + 6 = 96. FINDING: 4 more fits are non_converged
  (no per-fit frozen table survives, so which 4 is unknown). Per-fit spots: bmi.EUR.APOE_19q13 non_converged n_CS 6 =
  frozen (1/1). The 10 surviving 04-21 narrow-validation real-LD fits (FTO + SH2B3, EUR) match on status, n_CS and
  cs_sizes (10/10). They come from a pre-fire run, not the frozen fire.
- **Record tension (FINDING).** TRACK-A-FROZEN-NUMBERS.md:72 calls asthma "sole ok SH2B3 EUR fit". Both routes give
  t2d.EUR.SH2B3_12q24 ok (n_CS 9) as well, as does the 04-21 survivor, and :222 says asthma_vs_t2d was the only SH2B3
  EUR manifest row (the manifest admits only ok fits). Asthma ld_overlap_fraction 0.0385 is reproduced.
- Panel-absent EUR HLA_6p21 / BMI_Xq24 (10 fits): 9 exit early (4 too_many_variants HLA, 4 no_variants + t2d
  too_many_variants Xq24). bmi.EUR.HLA_6p21 is ok n_CS 10 with no panel. The frozen HLA fire used UKBB-LD tiles, so a
  per-fit difference there would come from the absent panel, not from code drift.
- Both routes ran in the same R env (r_coloc). Route C ≡ Route L therefore measures code drift only; environment drift
  since 04-22 is not tested. No policy or code was changed in response to any mismatch (§B.10).
- **Wave close** (LSF 432078, c017n03, HEAD 741f44b5). QUICK `346 passed, 52 deselected` (100 s). HEAVY `48 passed,
  4 skipped` (20m28s; same 4 W5a/W5b skips; the live known-answer test RAN). Pins `39 passed`. FULL 1872 ids / 1822
  passed / 50 skipped / 0 failed (38m31s, full_W3a.xml). Vs full_W2d.xml: common 1864, removed 0, added 8 (all
  test_known_answer_repro), changed 0; tests/m3 1299 unchanged. sparse_parent_benchmark.tsv restored.
  run_susie_rss.R 0-diff. A first close job (431883) stopped at QUICK: a `/rs1/researchers` literal in
  known_answer_compare.py (test_storage_on_rs1). Fixed with `R4_RSCRIPT` / PATH. Commit `26a6bb5f`.

## 2026-10-29 — W3b executed (SH2B3 R2-exact known answer, L10/iter-100, findings report); STOPPED at Task 3

Entry written 2026-11-02 from commit `0ef8b029`, `data/r4/logs/fire_w3b_sh2b3.log`, `data/r4/logs/lsf/`, `data/r4/logs/sh2b3_{r2,L10}/`
and the committed manifests. The W3b work itself ran 2026-10-29 02:20–02:43 EDT. `$W1` = `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md`,
`$W2` = `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md`.
- **(a) L15 fit code = `02c4404`.** `$W1:219` "21:51:00 — Rule 1 auto-fix applied to `src/legacy/region_analysis/scripts/run_susie_rss.R:38`;
  commit `02c4404`". The fits R2 used are the 2nd/3rd re-fire attempts after it (`$W1:223` "22:26:04 → 23:01:39 — third re-fire attempt …
  covered remaining 7 fits (1 L=15 stroke …)"). run_susie_rss.R blob ad2b3e3 at 02c4404, 299b52d and c0f02b6 (`git rev-parse`), i.e. unchanged
  through the R2 coloc; `git log 02c4404..c0f02b6 -- run_susie_rss.R config/susie_policy_L15.yaml` is empty.
- **(b) Policy = `config/susie_policy_L15.yaml` at 9c87157, max_iter_primary 500 / max_iter_retry 1000.** `$W1:216` "config/susie_policy_L{15,20,30}.yaml
  patched (max_iter_primary 100→500, max_iter_retry 200→1000); commit `9c87157`". `git show 02c4404:config/susie_policy_L15.yaml` lines 24–25
  `max_iter_primary: 500` / `max_iter_retry: 1000`; blob 09da798 at 9c87157, 02c4404 and HEAD.
- **(c) R2 coloc = `src/snakemake/scripts/run_coloc_susie.R` at `c0f02b6` (blob 4ed2599), la_multitrait_r Rscript.** `$W2:178` "- **Commit:** c0f02b6"
  (R.utils made optional, `$W2:172-177`); commit time 2026-04-29 23:43:43, and `$W2:63` "LSF dispatch TS=20260429_234353 (re-fire after R.utils
  Rule 1 auto-fix …)". Dispatcher `bin/fire_canonical_susie_pairs_W2_strategy3.sh` (`$W2:29`, `$W2:159`); its line 11
  `RSCRIPT=/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript`. la_multitrait_r `conda-meta/history` last entry 2026-04-24 17:31:08,
  so the env is unchanged since before R2. The R2 fits were swapped into the Stage-2 namespace (`$W2:155`).
- **Extraction** (`bin/r4_extract_legacy_code.sh`, now path-aware): legacy_code_sha256.tsv 2 + 5 = 7 rows (02c4404 script ×2 + policy; c0f02b6 ×2).
  arms.repro_sh2b3_r2 points at the extracted 02c4404 script and policy. commands.fit_command and ta_r4_finemap.smk unchanged. Commit `0ef8b029`.
- **Fire** (`data/r4/tmp/w3b_fire_chain.sh`, R4_R2_RSCRIPT = la_multitrait_r; serial queue). DAG 22 = 3 r4_run_finemap + 9 r4_sh2b3_r2_coloc +
  9 r4_sh2b3_L10_coloc + 1 r4_sh2b3_all (local). LSF submissions 21 + 1 re-fire = 22 (440330–440672); 440334 (L10 stroke_vs_t2d) died at LSF start ("Cannot open your job file",
  the W3a exit-255 pattern). At 20/22 the watchdog killed Snakemake, unlocked (`.snakemake/log/2026-10-29T023746…` "Unlocking working directory")
  and re-fired: 2 steps, 440672 completed. Dry-run "Nothing to be done" (re-checked 2026-11-02). L15 fits written 02:28:33 / 02:31:13 / 02:32:28.
- **Outputs**: 9 + 9 coloc JSONs; fits_repro_sh2b3_sha256.tsv 3 JSON + 3 fit.rds + 18 coloc = 24 rows (`sha256sum -c` OK 2026-11-02).
  L15 `.fit.rds` md5 903782e2 / 3dc6fe83 / 4c539b5a = the R2 post-swap md5s in `wave2_dispatch_tracker.json:28-30`.
- **R2_exact vs frozen R2** (known_answer_sh2b3.tsv, 18 rows = 9 R2_exact + 9 L10_iter100): match 9 + differ 0 = 9; `cmp` byte-identical 9/9.
  Fingerprint bmi_vs_hypertension n_cs 13 × 5, nsnps 168, hit1/hit2 rs3184504: 5/5. L15 n_CS 13/5/3, ld_overlap 170/589/622, all non_converged
  niter 1000 L_used 15, policy_hash 456efb68….
- **L10/iter-100** (separate measurement): bmi–htn 1.0 and htn–stroke 1.0 hold; htn–t2d 3.0943e-08 (R2 1.0).
- **New findings** (FINDINGS §4/§5/§8): JSON credible_sets vs `.fit.rds` `$sets$cs` eq 37 + differ 29 + no_sets 30 = 96, non-empty 51 vs 25;
  R1 28 pairs ≥ 1 side zero 14 (JSON) / 22 (rds), 6 FTO EUR pairs non-empty both sides; TRACK-A-FROZEN-NUMBERS.md:357/:361 cite a later commit
  and later fits; the R2 coloc skipped the chr:pos rewrite (18/18 logs, R.utils absent). No number adjusted (§B.10).
- Negative controls (2026-11-02, module restored by sha256): TOL 1e-6→1e-30 → `test_tolerance_1e6[5e-07-true]` FAILED; dropping the
  fingerprint_check from match → `test_bmi_htn_fingerprint_is_absolute_not_relative` FAILED. The original RED run is not on record.
- FINDINGS edits 2026-11-02: source paths added to §6 (effective max_iter 100, `$W1:218`, Route C niter) and to each §7 line. No number changed.
- **Wave close** (LSF 481675, c017n04, HEAD 0ef8b029, 2026-11-02). QUICK `360 passed, 54 deselected` (87.7 s). HEAVY `50 passed, 4 skipped`
  (21m44s; same 4 W5a/W5b skips; both W3b live tests ran). Pins `39 passed`. FULL 1888 ids / 1838 passed / 50 skipped / 0 failed (40m02s,
  full_W3b.xml). Vs full_W3a.xml: common 1872, removed 0, added 16 (all test_sh2b3_known_answer), changed 0; 1872 − 0 + 16 = 1888;
  tests/m3 1299 (1265/34) unchanged. sparse_parent_benchmark.tsv restored; run_susie_rss.R 0-diff. An earlier close (440842, 2026-10-29)
  gave the same ids/outcomes (full_W3b.440842.xml). Commit `57ed36a8`.
- **Task 3 (W3b-T3, Carter human-action) NOT started.** No sign-off recorded.

## 2026-11-02 — W3b-T3 signed off (Carter)

Reply, verbatim:

```
carter-approved 2026-11-02
instructions: proceed. 1. ive read it, 2. lets fix these mismatches, what are the causes? 3. confirm unless there is a reason to use a different one. 4. findings dont change the pre-reg
```

`signoffs/W3b-T3.yaml` raw_sha256 e8800b8e…; `signoff verify W3b-T3` exit 0. D-17 SH2B3 provenance statement confirmed.
Pre-registration (W4a) unchanged by the findings. Follow-up: cause analysis of the W3 mismatches (no number adjusted, §B.10).

## 2026-11-02 — quick-261102-log Task 1: W3 errata + FINDINGS causes

- TRACK-A-FROZEN-NUMBERS.md: `## ERRATA (2026-11-02)` appended, E1–E7 (additions only; `git diff` 14 added / 0 deleted lines).
- FINDINGS §4 (4 fits named: asthma/bmi/hypertension/t2d.EUR.FTO_16q12, identity-placeholder FTO LD in the 04-22 fire;
  env-drift caveat no longer needed), §7 items 3/4/9 updated, items 10 (JSON `credible_sets` unfiltered; fix pending Carter's
  D-28 decision, Task 2) and 11 (latent chr:pos alignment defect, open) added, §8 measured cause (R1 read V4 fits).
- Counts re-measured from `$MAN/fit_cs_json_vs_rds.tsv`: eq 37 (22 non_converged + 15 ok) + differ 29 (ok) + no sets 30 = 96;
  non-empty JSON 51, rds 25, JSON-only 26; 51 − 26 = 25. Status: 44 + 4 = 48 ok, 22 − 4 = 18 non_converged (debug file).
- cs_sizes writer check (E1): `grep -rn IDENTITY-LD-K2D-FIT-SUMMARY bin src` = readers only (fig2/fig3, ta_r4, repro bundle);
  no writer in code. The TSV was written in ec86832e (quick-260425-ieh), whose PLAN :161 says "len(cs) for each cs in
  JSON.credible_sets". Current `summarize_finemap_results.py` `summarize_file` on
  `repro_k2d_routeC/.../stroke.EUR.SH2B3_12q24.json` gives `CS1:1;…;CS8:1;CS9:19;CS10:38` = `len(v)` per set; the record
  row is `3;3;3;3;3;3;3;3;3;4` = `len(key)`. Verdict: not present in current code; no Task 3 sub-step needed.
- No code, fit or frozen number changed (§B.10). `run_susie_rss.R` untouched.

## 2026-11-03 — W3c simulation harness (code + config + tests; no production run)

- Precondition: `signoff verify W3b-T3` exit 0. Carter's instructions: none concern the simulation design; item 4 ("findings dont
  change the pre-reg") applied — design values as in the plan.
- **Harness commit `0efac930`** (cite in the W4a amendment): simulate_coloc_r4.R, simulation.yaml (locked: false), ta_r4_sim.smk,
  run_coloc_pair_r4.R main-guard refactor (coloc_pair_core), tests/ta_r4/test_simulation_harness.py (21 tests: 11 quick, 10 r4_heavy).
- Harness SuSiE = run_susie_rss.R's `%||%`, `regularize_ld`, `run_susie_with_ladder`, parsed from the frozen file at load time (not copied).
  run_susie_rss.R 0-diff vs 53106f8.
- RED: 4 failed + 17 errors (harness file absent, simulation.yaml absent, no rule). GREEN 21 passed.
- SuSiE identity vs the frozen script via commands.fit_command (fixture, 60 variants): max|dPIP| 0.0 A2_identity (5 CS = 5) and A3_1kg (1 = 1).
  Coloc identity vs the run_coloc_pair_r4.R CLI on the harness's fits (A1_matched, A2 susie, A3 susie): max|dPP| 0.0.
- W0d CLI before/after the refactor (4 fixture regions x 2 p12 keys x 3 modes = 24; 20 JSON + 4 UNMAPPED_FIT_NAMES refusals):
  parsed-dict diff empty; snapshot files byte-identical.
- Negative controls (8, `-B -p no:cacheprovider`, each restored sha256-identical): frozen call + estimate_residual_variance=TRUE,
  L-5, harness p12_sensitivity, no PSD clip, seed +1, H3 bin ignored, rule without gate, rule passing --reps-override → each RED.
- Config key `n_per_trait` (not `n`): R yaml parsed `n:` as FALSE → harness n = numeric(0) → every susie_rss errored. Harness now refuses
  non-positive/missing numeric config keys.
- Gate: `bash bin/r4_fire.sh production A3_1kg -n data/r4/results/sim/SH2B3_12q24.H4.gen_1kg.tsv` rc 1,
  `LockGateError: (a) lock record absent`. Fixture-repo dry runs: no lock → refused; with fixture lock → 100 r4_sim jobs, no --reps-override.
- Smoke (pre-gate; not an estimate): SH2B3_12q24 gen_1kg H4 and H3_r2_0.6, `--reps-override 2`, data/r4/tmp/sim_smoke/ (window 745,
  6 rows each; H3_r2_0.6 qualifying pairs 4782; seed rep 1 H4 = 20278622 = 20261021 + 17601).
- **Scheduler: Slurm from 2026-11-03 (Carter); LSF no longer used.**
- **Wave close** (Slurm 1672481, c207n03, HEAD 0efac930, 1h05m). QUICK `371 passed, 67 deselected` (97 s). HEAVY `63 passed, 4 skipped`
  (21m44s; same 4 W5a/W5b skips). Pins `39 passed`. FULL 1912 ids / 1862 passed / 50 skipped / 0 failed (41m56s, data/r4/tmp/w3c/full_W3c.xml).
  Vs full_261103.xml by id: common 1891, removed 0, added 21 (all test_simulation_harness, all passed), changed 0; 1891 − 0 + 21 = 1912;
  skips 50 = 50 same ids; tests/m3 1299 (1265/34) unchanged. sparse_parent_benchmark.tsv clean.

## 2026-11-03 — W3d estimators, branch classifier, coverage, aggregation (code + config + tests; no production data)

- **Analysis-code commits (cite in the W4a amendment, with W0d/W3c/W3e):** `db2bf8c9` (estimands.py, branch_classifier.py,
  cs_cross_purity.R, decision_rules.yaml draft locked: false), `83b3240d` (coloc_coverage.py), `bd551895` (run_aggregation.py),
  `aef3be84` (Rscript from PATH, not an /rs1 literal).
- Real manifest: confirmatory rows 100 over 10 region_safe clusters. Coverage expected EUR 290 × 2 × 7 = 4060 and AFR 30 × 2 × 5 = 300;
  real-repo CLI `missing=4060` / `missing=300`, rc 1 (no outputs yet).
- Truth table: 36 combos; via rule1 18 / rule2 6 / rule3 4 / partial_rule 8. Branches excluding partial_rule: NON_INFORMATIVE 18,
  NO_SYSTEMATIC_DIFFERENCE 3, HETEROGENEOUS 3, INFLATION_SUPPORTED 2, DEFLATION 2.
  - The 8 partial rows are (pos, ns), (pos, sig_A3_gt_X), (neg, ns) and (neg, sig_X_gt_A3), each × kappa_ok. They are governed by 4
    keys, all drafted HETEROGENEOUS.
  - These keys, plus kappa_cut, n_both_min and the confirmatory block, are Carter's decisions in W4a-T3.
- REDs: T1 49 failed + 33 errors; T2 6 failed; T3 6 failed + 4 errors.
- Negative controls (each RED, restored sha256-identical):
  - T1 (4): partial key deleted, precedence swapped, row bootstrap, NC rows in the filter.
  - T2 (2): `check()` drops missing; CLI with one file removed exits 1.
  - T3 (4): gate removed, coloc globbed from every results dir, `import math`, NC leak into the confirmatory filter.
- Cluster bootstrap vectorized (bit-identical to the per-draw loop on the same picks) to hold QUICK under 120 s.
- **Wave close run 1** (Slurm 1674027, HEAD bd551895): FULL 1 failed, `test_storage_on_rs1::test_no_rs1_or_share_literals_in_r4_config_and_src`
  (an /rs1 Rscript literal in run_aggregation.py). The code was fixed in aef3be84; the test is unchanged.
- **Wave close run 2** (Slurm 1674938, c207n09, HEAD aef3be84, 59m36s):
  - QUICK `470 passed, 67 deselected` (118 s).
  - HEAVY `63 passed, 4 skipped` (same 4 W5a/W5b skips).
  - Pins `39 passed`.
  - FULL 2011 ids / 1961 passed / 50 skipped / 0 failed (`data/r4/tmp/w3d/full_W3d.xml`).
- **By id vs full_W3c.xml:**
  - Removed 0, added 99 (all passed: contrast_stats 33, branch_classifier 24, estimands 22, run_aggregation 10, coloc_coverage 6,
    cs_cross_purity 4), changed 0; 1912 − 0 + 99 = 2011.
  - Skips: the same 50 ids. tests/m3: 1299 (1265/34), unchanged.
  - fsck: dangling only. sparse_parent_benchmark.tsv clean.

## 2026-11-04 — W3e QTL harmonization (pre-gate) + group runner (code + config + tests; no QTL coloc on real data)

- **Analysis-code commits (cite in the W4a amendment, with W0d/W3c/W3d):** `4d27ac00` (harmonize_qtl_r4.py, r4_qtl_harmonize,
  qtl_harmonized_sha256.tsv), `0ca16af9` (run_qtl_group_r4.py, run_coloc_pair_r4.R --mode qtl_abf, r4_qtl_group /
  r4_qtl_aggregate / r4_qtl_tiers / r4_qtl_all). **`0ca16af9` is the last analysis-code commit of W3.**
- **Harmonization fire** (D-05, pre-gate): `bin/r4_fire.sh repro repro_routeC` inside Slurm 1675878 with a local profile and a
  refusing `bsub` shim (no LSF; `Provided cores: 8`). Result: 899 groups, `900 of 900 steps (100%) done`, 13.5 min, then
  `Nothing to be done`.
  - Files: 23,310 = distinct (source, qtd, molecular_trait_id, region) manifest features 23,310 (eqtl 21,149 + sqtl 2,161).
  - 0 empty; 0 rehash mismatches; 91,853,028 harmonized rows.
  - `$MAN/qtl_harmonized_sha256.tsv` has 23,310 rows.
- **Deviation: sQTL per junction.** The shipped `harmonize_sqtl()` filters on gene_id, so gene-level files mix the junctions of
  376 genes (882 junctions). The plan's gene_id count, 22,804, is lower by 882 − 376 = 506. The wrapper cuts the window per
  molecular_trait_id and runs the shipped function. eQTL output equals the shipped CLI; sQTL junction files partition the shipped
  gene-level rows. **Finding for W4a:** the frozen layer's sQTL rows for multi-junction genes were mixed.
- **Runner:** QTL_A3 (A3_1kg, EUR_1kg_r4, join + orient), QTL_A2 (A2_identity, EUR_identity_r4, same flags) and QTL_legacy
  (repro_routeL, legacy_repro, `--ld-allele-join false`, no `--variant-list`, no `--qtl-orient`).
  - No-CS rows get fallback_abf via `run_coloc_pair_r4.R --mode qtl_abf`, on the bridged set run_qtl_coloc.R uses (equality
    tested by tracing `coloc::check_dataset`).
  - Fixture group: 1 coloc_susie and 3 fallback_abf (qtl_n_cs==0 / gwas_n_cs==0 / both) in both arms.
  - Coverage exits 1 naming any missing or extra row.
- **Dry runs (HEAD 0ca16af9):**
  - `production A3_1kg -n <QTL_A3 group>`: rc 1, `LockGateError: (a) lock record absent`.
  - `repro repro_routeL -n <QTL_legacy group>`: 1 r4_qtl_group job.
  - `repro repro_routeL -n r4_qtl_all`: 1002 jobs (899 groups + 100 routeL trait-pair coloc + aggregate + tiers + all).
- **REDs:** T1 ImportError (collection); T2 `15 failed, 15 passed` (R mode and rules absent).
- **Negative controls** (each RED, restored sha256-identical):
  - T1 (2): no junction cut, reader not restored.
  - T2 (8): fallback mislabelled, legacy `--qtl-orient`, coverage drops missing, bridge keeps orientation drops, bridge keys on
    chrpos, abf on p12_sensitivity, QTL gate removed, every R failure becomes a row.
- **W0d** CLI snapshot before/after the run_coloc_pair_r4.R refactor: 24 outputs, byte-identical.
- **Wave close** (Slurm 1677128, c024n04, HEAD 0ca16af9, 56m45s):
  - QUICK `491 passed, 83 deselected` (108 s). Vs W3d: +21 quick (harmonize 7, runner 14), +16 heavy (runner 9, qtl_abf 7).
  - HEAVY `79 passed, 4 skipped` (63 + 16; the same 4 W5a/W5b skips).
  - Pins `39 passed`.
  - FULL 2048 ids / 1998 passed / 50 skipped / 0 failed (`data/r4/tmp/w3e/full_W3e.xml`).
- **By id vs full_W3d.xml:**
  - Removed 0, added 37 (all passed: test_qtl_group_runner 23, test_coloc_pair_r4 7, test_qtl_harmonize_r4 7), changed 0;
    2011 − 0 + 37 = 2048.
  - No passed→skipped. tests/m3 1299 (1265/34), unchanged.
  - fsck: dangling only, before and after each commit. sparse_parent_benchmark.tsv clean.
- **For W4a (Carter):** sQTL unit = junction (frozen-layer finding); tiers count coloc_susie rows only (fallback_abf reported, not
  tiered); QTL_legacy tier input = routeL trait-pair coloc via run_coloc_pair_r4.R; below-floor rows kept as method none;
  run_qtl_coloc.R uses the coloc.susie package priors (= yaml now; a p12 change needs a priors flag before the lock).
- **For W6:** bin/r4_fire.sh still carries the LSF profile. Fire under Slurm with a second `--profile` (local) and a bsub shim,
  or add a Slurm profile. 899 group jobs per QTL arm; per-row cost on real windows is unmeasured.

## 2026-11-04 — W4a Task 1 (extractor + text tests, R4 amendment DRAFT, deviations entry)

- **p12 citation (verified).** Wallace 2020, "Eliciting priors and relaxing the single causal variant assumption in
  colocalisation analyses", PLoS Genet 16:e1008720. Source: JATS XML from
  `https://journals.plos.org/plosgenetics/article/file?id=10.1371/journal.pgen.1008720&type=manuscript` (sha256
  b6af1f883af8eaf2eefd85247a3683e8b54daa8fdc2d68e06b822ab49b8c4347; scratch only). Exact sentences:
  - Results: "The results suggest that the coloc default of p12= = 10−5 may be overly liberal, with data simulated under H3
    having posterior support for H4, particularly for smaller samples, and that p12 = 5 × 10−6 may be a more generally robust choice."
  - Discussion: "Perhaps the most widely applicable are the results of simulations, that suggest values of the order
    p12 ≈ 5×10−6 lead to robust inference over a range of scenarios, but the adoption of sensitivity analysis will help
    evalutate robustness of inference to changes in prior parameter values."
  - ⚠ Closing summary (conflicts): "The simulations here (Fig (4)) suggest that p12 = 5×10−5 provides a reasonable balance
    between power and false positive calls, but it is unlikely that any single point distribution on p12 captures all prior knowledge."
  Two sentences support 5e-6; the summary prints 5e-5 (probable typo, not verified). 5e-6 kept as the PROPOSED value; the
  conflict is stated in the DRAFT §(f) and goes to Carter at W4a-T3.
- **Plan vs code (measured before writing).** The W0d "Decision needed" (fit-name alignment) is still open in code:
  `run_coloc_pair_r4.R --mode susie` on repro_routeC SH2B3_12q24 hypertension × stroke →
  `Error: UNMAPPED_FIT_NAMES: fit_a: 589 of 589 fit variant names (e.g. rs7961935) are neither a sumstats SNP_ID nor
  CHR:POS in SH2B3_12q24 (LD-panel rsid override?)`, rc 1. Fit names (repro_routeC SH2B3 EUR): hypertension 589/589 rsid,
  stroke 622/622, t2d 863/863, asthma 147/147, bmi 170/170. hypertension/stroke/t2d sumstats are chr:pos (W2a). So
  production coloc refuses most EUR pairs as coded. Carried to W4a-T3 as an open decision; the DRAFT §(d) has a
  ‹CARTER-LOCK› placeholder for the rule. Nothing changed in code.
- **Plan vs record.** (h)'s R1 line follows FINDINGS §(8) (measured: non-empty PP.H4 0/28; 22/28 zero purity-filtered
  sets on ≥1 side; 3 FTO pairs reached coloc.susie), not the plan's shorter "no_signal, n_cs 0" wording. (m) names the
  phase-dir panel manifests as `manifests/panels_*.tsv` (the internal-content scan bans `.planning/`); the text test maps
  that LOCKED_PATHS entry the same way. The A3-UKB panel is Weissbrod 2020 UKB 337k (data_sources.yaml), not Pan-UKBB.
- **RED** (`data/r4/tmp/w4a/red_t1.txt`): `ImportError: cannot import name 'extract_paste_block'` (collection error).
  **GREEN:** `19 passed, 2 skipped` (FINAL/PUBLIC absent, reason printed).
- **Negative controls** (`data/r4/tmp/w4a/nc_t1_out.txt`; files restored sha256-identical):
  NC1 "pivot" in DRAFT extract → `test_draft_extract_framing` failed; NC2 ".planning/x" → `test_draft_extract_internal_content`
  failed; NC3 decision_rules.yaml clusters → `row_id of ...` → 2 failed (confirmatory NC + rendered-block test). In-file NCs
  (tmp extracts with "Pivot", ".planning/x", checklist/CARTER-LOCK, end-before-start) pass as tests.
- **DRAFT** extract 2,514 words (≤ ~2,700). Confirmatory sentences pasted from `render_confirmatory(rules)` unchanged.
- **osf_deviations.md** "R4 amendment — DRAFTED, NOT POSTED" appended; `git diff | grep -c '^-[^-]'` = 0.

## 2026-11-04 — W4a Task 2 (brief-blind Codex review of the extract; dispositions; DRAFT fixes)

- Review input: `extract_paste_block --in DRAFT@a4090fa6 --out data/r4/tmp/w4a_review_input.md` (sha256 95a5f928…). Prompt =
  the plan's instruction + that extract only (sha256 34620f5c…). No CONTEXT/RESEARCH/LOG/summary was given.
- Attempt 1 (codex-cli 0.141.0, config model gpt-5.5): rc 1, empty output, "model is not supported when using Codex with a
  ChatGPT account". Probed gpt-5/5.1/5.2/5.3/5.4 codex names: all rejected. `~/.codex/models_cache.json` lists gpt-6.x.
  codex-cli 0.166.0 installed into a scratch prefix (shared gsd-tools env untouched). Attempt 2: `-m gpt-6.1-sol`, rc 0,
  40,055 B (sha256 697bfd1f…). Banked verbatim (embedded-bytes check True) in `ta-r4-W4-AMENDMENT-REVIEW-as-received.md`.
- Findings 31 (18 numbered + 13 table qualifications) = 31 disposition rows. Verified myself: cap order run_susie_rss.R:946
  before :1042; R4 catalog PYHIN1_1q23 98,393 rows; asthma×PYHIN1 catalog-joined 38,313 (> 16,000) → `too_many_variants` →
  run_coloc_pair_r4.R FIT_EARLY_EXIT; LOCKED_PATHS lacks config/susie_policy.yaml (read by arms.py:6) and config/pipeline.yaml
  (bin/r4_fire.sh:71); kriging rule :1297; ladder 3 steps; susieR 0.14.2 estimate_residual_variance default FALSE (measured);
  UKB n_samples NA; BMI_5q13_3 isect zero-filled 8,635,830; aggregate_qtl_coloc reads `summary` only; sim identity refit :61-64.
- DRAFT: 26 text replacements so the text describes the code (one script, each match asserted unique); new ‹CARTER-LOCK›
  early-exit rule in (d); Pre-Paste OPEN row. `test_amendment_text.py` 19 passed / 2 skipped after. Extract 2,799 words
  (over the ~2,700 guide by ~100; accuracy additions, not trimmed).
- No analysis code changed. Carter decisions before the lock: N1, N2, N3, N4, N5, N6, N7, N8, N12, N14, T1 (+ optional N9, N10).
- **§C wave close (W4a-draft; Slurm 1680976, c205n03, HEAD a4090fa6 + uncommitted DRAFT/review edits, 1h35m):**
  QUICK 510 passed / 2 skipped / 83 deselected in 150.5 s (> 120 s); HEAVY 79 passed / 4 skipped (same 4 W5a/W5b skips);
  PINS 39 passed; FULL 2069 ids = 2017 passed + 52 skipped + 0 failed (`data/r4/tmp/w4a/full_W4a.xml`).
  By id vs full_W3e.xml: common 2048, removed 0, added 21 (all test_amendment_text: 19 passed + 2 skipped), changed 0;
  2048 − 0 + 21 = 2069. tests/m3 1299 (1265 / 34) unchanged. sparse_parent_benchmark.tsv clean.
- **QUICK budget:** `--durations` on the login node: `test_import_isolation.py::test_m3_conftest_import_still_works` 68.67 s
  (next slowest 5.72 s). Marked `r4_heavy` (marker only; still runs in HEAVY and FULL; passes, 24 s). QUICK re-timed:
  509 passed, 2 skipped, 84 deselected in 91.9 s.

## 2026-11-04/05 — W3f 15.1 (N1 cap after LD restriction; N2 fit-name alignment; N8 method none)

- DECs: DEC-2026-11-04-ta-r4-w3f-fix-all, DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor,
  DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze.
- Commits: e38a519c, 4a1b9d4a (decisions); 6c6e9546 + 1f771281 (N1, two code commits) with re-pins 3e895261, e5792b8b;
  7a3415df (N2 + N8); 215ddde3 (differential-substrate argv fix).
- RED/GREEN/NC under `data/r4/tmp/w3f/`: t2_red 5F/1P → t2_green 6P; t2_nc1, t2_nc2 1F each; t3_red 30F + 2E;
  t3_nc1 3F, t3_nc2 1F, t3_nc3 1F.
- SH2B3_12q24 hypertension × stroke: 589 = 0 direct + 589 panel_exact + 0 swapped + 0 strand; 622 = 0 + 622 + 0 + 0; n_snps 583, rc 0.
- Close (Slurm 1716306): plan verify 104P/1S; QUICK 531P/2S in 185.9 s (over the 120 s budget); HEAVY 1F/95P/4S →
  test_fit_rds_unchanged_by_the_fix (pre-fix 656529a rejects the N1 flag) → 215ddde3 → 3P (Slurm 1717387); PINS 39P.

## 2026-11-09 — W3f 15.2 (N3 locked paths; N4 in-job input sha256; N5 in-job gate; T1 label)

- Commits: 82490835 (N3), 6312db61 (N4), d61fb081 (N5 + r4_fire.sh + T1). Pushed to origin/m3-W2-aou-deltas.
- **N3 dependency measurement** (grep of quoted repo paths across Snakefile.ta_r4, ta_r4_*.smk, ta_r4/*.py, bin/r4_fire.sh;
  `source(`/`file.path(` in the R scripts; repo-local imports of the ta_r4 modules and shared helpers). Live non-data reads not
  previously locked: config/susie_policy.yaml (arms.py:6), config/pipeline.yaml (Snakefile.ta_r4:14, r4_fire.sh --configfile),
  src/snakemake/scripts/qtl_orient.R (run_qtl_coloc.R:184-188, run_coloc_pair_r4.R:346), config/qtl_sources.yaml
  (harmonize_qtl_r4.py:29), src/python/build_tissue_n_lookup.py (harmonize_qtl_r4.py:22), config/pph4_thresholds.yaml
  (ta_r4_qtl.smk:141); plus, found by the measurement: manifests/{sumstats_r4,catalogs,qtl_harmonized}_sha256.tsv (read by
  the N4 in-job check) and manifests/known_answer_{W3a,sh2b3}.tsv (run_aggregation.py:27-28). 6 + 5 = 11 entries appended.
  Not added (builder inputs whose outputs are locked or hash-checked): config/negative_controls.yaml (build_pair_manifest →
  pair_manifest.tsv, locked), config/regions_curated_grch38.csv + review_decisions (build_qtl_manifest → qtl_manifest.tsv,
  locked), config/eqtl_catalogue_qtd_map.yaml + manifests/qtl_downloads_sha256.tsv (pre-gate downloads/harmonize → harmonized
  files, sha-checked in-job), collect_region_variants.py / build_ld_rds.py / ukb337k_tiles (catalogs sha-checked in-job;
  panels md5-checked by write_ld_receipt). Enforcer: test_lock_gate.py::test_every_measured_dependency_is_covered_by_locked_paths
  (41-entry R4_DEPENDENCIES).
- **N4 input listing** (production arms, admissible pair_manifest rows + QTL manifest rows): sumstats 8 listed / 8,
  catalogs 29 / 29, harmonized QTL 23,310 / 23,310 (116,550 qtl_manifest rows). Repro arms: sumstats 8/8 but catalogs 10/29 —
  unlisted = 19 data/r4/ld/variants_legacy/NC_*.tsv → verification applied to production arms only (repro renders `true`);
  QTL_legacy inputs are all listed, so run_qtl_group_r4 verifies every QTL arm. Cost: stroke.EUR 137 MB verifies in 0.8 s.
- RED/GREEN/NC under data/r4/tmp/w3f2/: t1_red 13F → t1_green 77P/2S; t1_nc (susie_policy removed) 3F.
  t2_red collection error, t2_red2 11F/10P → 21P; t2_nc1 (skip unlisted) 2F; t2_nc2 (no verify in run_group) 4F.
  t3_red 16F/3P; fire RED with old DIRTY list (susie_policy dirty → rc 0, SMK called); globbing-on RED (deleted ta_r4_b.smk
  missed) → set -f → 5P; t3_green 19P (gate rc 0 before drift, 1 after); t3_nc1 (gate only in finemap) 6F/1P; t3_nc2 2F.
- Task 2 verify Slurm 1782976: 64 passed. Close Slurm 1783263 (c203n05, tree = d61fb081 less the aggregation fixture fix):
  plan verify T3 104P; HEAVY 115P / 4S (the W5a/W5b skips) in 29m15s; PINS 39P; QUICK 566P / 1F / 2S —
  test_run_aggregation::test_final_label_with_fixture_lock_and_signoff: its fixture left the now-locked known-answer tables
  untracked → gate (h) → status DRAFT. Fixture now commits them (assertions unchanged). QUICK rerun Slurm 1783856: 567P / 2S
  in 137.7 s (566 + 1 = 567; over the 120 s budget, carried to 15.6). FULL not run (plan §C list: QUICK, HEAVY, PINS).

## 2026-11-09 — W3f 15.3 (N7 region sign-flip test + n_regions_min 7; N6 completeness + coverage-gated FINAL)

- Commits: 92caa306 (N7), 0ac1a15e (N6), a36d4ad1 (DRAFT (e) render). Pushed 0ad0b742..a36d4ad1.
- confirmatory_sha256: old f6e6e90f83fd14975d3afa04789c3dcf1a9211b8e3ddd38bf23c72f8cbe0e9e3 (from
  `git show 0ad0b742:config/ta_r4/decision_rules.yaml`) -> interim 9fa410aa411fc2c682a4886dd25ca98d5dfd37f6968ecffc1a0a8860003888d5.
  Command (cwd src/python): `$PY -c "import yaml; from ta_r4.signoff import canonical_sha256;
  print(canonical_sha256(yaml.safe_load(open('../../config/ta_r4/decision_rules.yaml'))['confirmatory']))"`. Final value: 15.5.
- Counterexample A (10 rows of one region of 100) on 0ad0b742: ('INFLATION_SUPPORTED', 'rule3_agree'), n_both 10, CI
  [0.2, 0.2], McNemar p 0.001953125. After N7 alone it is NON_INFORMATIVE, but a cherry-picked set (one row per region over 10
  regions) is still INFLATION_SUPPORTED (signflip p 0.001953125). After N6 both raise ConfirmatoryIncomplete. Counterexample B
  (10-row manifest): ('NON_INFORMATIVE', 'rule1_n_both'), n_regions 1.
- RED/GREEN/NC under data/r4/tmp/w3f3/: t1_red 31F/80P -> t1_green 111P; t1_nc1 (row McNemar) 9F, t1_nc2 (no region term) 5F,
  t1_nc3 (> for >=) 17F. t2_red 27F/34P -> t2_green 91P; t2_nc1 (ids from rows) 2F, t2_nc2 (no coverage) 3F. t3_red 5F/16P/2S
  -> t3_green 62P/2S; t3_nc (renderer hard-codes 7) 1F (path0-6 only).
- Truth table: 18 NON_INFORMATIVE / 3 NO_SYSTEMATIC_DIFFERENCE / 11 HETEROGENEOUS (3 + 8) / 2 INFLATION_SUPPORTED / 2 DEFLATION = 36.
- Close Slurm 1784345: plan verify 111P / 61P / 62P+2S; QUICK 612P/2S in 189.2 s (567 + 45 new = 612; over 120 s, for 15.6);
  HEAVY 115P/4S in 32m00s; PINS 39P. FULL not run.

## 2026-11-09 — W3f 15.4 (N8 row_drops; N9/N10 widened E4/E6; N12 QTL fallback export; N14 simulation)

- Commits: ade4e9c5 (N8/N9/N10), bed315d4 (N12), 4d11c047 (N14). TABLES 17 -> 19 (+row_drops, +qtl_rows).
- RED/GREEN/NC under data/r4/tmp/w3f4/: t1_red 14F/32P -> t1_green 46P; t1_nc1 (status == ok) 1F, t1_nc2 (old e6) 2F,
  t1_nc3 (fallback as none) 2F (raises). t2_red 11F/49P, t2_red2 5F/1P -> t2_green 60P; t2_nc0 (unconditional columns) 1F,
  t2_nc1 (summary-only PPs) 1F, t2_nc2 (fallback tiered) 2F. t3_red 13F/35P -> t3_green 81P; t3_nc1 (identity refit) 2F,
  t3_nc2 (pooled) 2F, t3_nc3 (cell check off) 8F.
- Track B (phase2 tier/qtl_coloc/sweep + track_b_isolation): 67P before (HEAD script) and 67P after. Default
  aggregate_qtl_coloc output byte-identical to 319ae8f1.
- QTL tier equality (full vs tierable): tier and best/resolving columns equal. Measured: all_supporting_sources narrows to
  sources with coloc_susie rows; the sweep no longer counts a region without coloc_susie rows as Tier C (NaN comparison in
  assign_tier), n_tier_c 1 -> 0 on the fixture at all 4 thresholds.
- Committed simulation.yaml: expected_sim_cells = 100 cells, reps 200.
- Close Slurm 1785577: plan verify 49P / 60P / 48P; QUICK 644P/2S in 181.0 s (612 + 32; over 120 s, for 15.6); HEAVY
  116P/4S in 32m51s; PINS 39P. FULL not run.
- For 15.5: DRAFT (e) E4/E6, (g) identity refit and pooling, (l) QTL fallback wording and the OPEN row still describe the
  pre-15.4 code.

## 2026-11-16 — W3f 15.5 (eligibility measurement; region-contribution proxy; DRAFT) — STOPPED AT A CARTER DECISION

- Resumed (third executor) from uncommitted WIP; the 11-09 stale eligibility manifest moved to
  data/r4/tmp/w3f/elig_20261116/STALE_20261109_w3f_fit_eligibility.tsv (not committed). Code + tests f33a582c.
- Tests: RED 32F/28P (missing features) -> GREEN 60P quick + 4P heavy. NC (all RED, module restored byte-identical):
  cap 16000 kept 2F; --output left at fit_json 2F; no extra-key check 1F; no bound check 1F; no asthma exclusion 1F;
  no pin check 1F. Zero-overlap panel under cap 0 stops LD_DECLARED_REJECTED (no fit, no RDS) — review item 4.
- Measurement: run list 83 = A3_ukb 15 + 3 AFR arms x 6 + 50 A3_1kg EUR primary fits (pre-fix recount; includes both
  regression keys). Slurm 1946095 (cascadelake, 1 h, 32G): 83/83 COMPLETED 0:0, max RSS 9.5 GB, 83 JSON + RDS +
  inputs records; summarise() accepted all 83 (exact run list, early exits, no lbf_variable); input sha256 == pins 83/83.
  `find -L data/r4/results -newer data/r4/tmp/w3f/elig_20261116/meas/run.sh -type f | wc -l` = 0.
- FINDING (blocks the lock): eligibility_table() raises BoundViolation — A3_1kg asthma 9p21_CDKN2A n_variants 10,399 >
  panel n_var 7,576. Cause measured: r4 catalogs list one CHR:POS:REF:ALT under two SNP_IDs (chr:pos form + rsid form),
  30 of 31 catalogs, 248,257 extra rows of 877,756; run_susie_rss.R's allele-key catalog join copies the sumstats row per
  catalog row and nothing dedups before run_susie_with_ladder (read :760-1250). Independent reproduction of the join
  (Slurm 1946449, dup/decomp_all.R) equals the script's n_variants and n_variants_pre_ld on 83/83; distinct counts <=
  panel n_var on 83/83; every measured fit carries duplicates. Downstream run_coloc_pair_r4.R:440 would stop such pairs
  with DUPLICATE_KEYS. Repro (legacy SNP_ID join) arms are not affected by the 4-key duplication.
- Counts (current code / duplicates removed), post-restriction > 16,000:
  A3_1kg 50 primary fits: 4 / 0 (asthma, t2d x BMI_5q13_3, PYHIN1_1q23) -> primary rows hit 14 / 0
  (2 regions x (10 - C(3,2)) = 2 x 7 = 14). A3_ukb 6 / 4 of 15 (dedup: asthma, t2d x BMI_5q13_3, PYHIN1_1q23).
  AFR661_A3, AFR661_A2, AFR504_A3 each 4 / 2 of 6 (dedup: asthma x BMI_5q13_3, PYHIN1_1q23).
  Pre-fix (pre-LD rows > 16,000) on current inputs: 12 A3_1kg fits (asthma, t2d x 9p21, APOE, BMI_5q13_3, CXADR,
  PYHIN1, SLC2A9) -> 6 x 7 = 42 rows (review: 10 fits -> 35 rows on earlier inputs; CXADR added by the corrected
  asthma); duplicates removed 11 -> 39.
  Regression asthma x PYHIN1_1q23 A3_1kg: n_variants_pre_ld 63,742 (> 16,000), n_variants 22,038 > panel 15,236
  (bound VIOLATED), 12,605 distinct. t2d twin: 57,209 / 21,999 / 12,584.
- Region-contribution proxy ($MAN/w3f_region_contribution_proxy.tsv; repro_routeC / repro_k2d_routeC fits; asthma pairs
  excluded, 4 of 10 per region, because the repro fits read the GRCh38-mislocated asthma EUR file; proxy only, earlier
  panels/policies/joins, never a lock input): A1_matched_vs_A3_1kg likely 8 / unknown 1 / unlikely 1;
  A2_identity_vs_A3_1kg likely 3 / unknown 2 / unlikely 5 (sums 10). Discordance k: no repro coloc outputs exist, so k
  is unknown; bound A1 k <= 9, A2 k <= 5.
  FLAG FOR CARTER: n_regions_min 7 may yield NON_INFORMATIVE for A2_identity_vs_A3_1kg (likely 3/10, unknown 2)
  FLAG FOR CARTER: likely discordant regions k <= 5 < 7 for A2_identity_vs_A3_1kg (k unknown: 0 true, 5 unknown); the sign-flip test cannot reach alpha 0.025 with k < 7 (min p = 2/2^k)
  n_regions_min not changed.
- confirmatory_sha256: old f6e6e90f83fd14975d3afa04789c3dcf1a9211b8e3ddd38bf23c72f8cbe0e9e3 -> new
  9fa410aa411fc2c682a4886dd25ca98d5dfd37f6968ecffc1a0a8860003888d5 (== 15.3 interim). Truth table 18/3/3/2/2/8 = 36.
- DRAFT (partial): (c) asthma pins -> strand lifts 49edfc54 / 8828df14 + liftover disclosure; (h) repro-arm asthma
  disclosure; (k) cap after restriction to the panel + cascadelake/OpenBLAS kernel pin; (m) + 05921ac7, 3b1ff91f,
  bc5231c6, 520ed70f; Pre-Paste panel sizes (rebuilt), measured counts, OPEN duplicate-key row, proxy + FLAGs, sha.
  Re-verified unchanged: 8,635,830 (isect panels not rebuilt), EUR 1kG/identity manifests unchanged since b266e1d8,
  LOCKED_PATHS 29. test_amendment_text 21P/2S. Extract 3,998 words (2,945 at HEAD; target ~3,100). The (k)
  measured-count clause waits on the duplicate-key decision.
- QUICK (Slurm 1946214): 719P/2S in 208.6 s (over 120 s; for 15.6).

## 2026-11-18 — W3f 15.5a (r4 catalogs one row per normalized allele key; flag-gated run_susie_rss.R guard; rebuild + re-pin)

- Decision: Carter "1. Fix both ends (recommended)." (`W3f-carter-dupkey-fix-reply-2026-11-17.txt`, sha256 72a6254a…6653;
  hand-back sha256 cb52ce1a…5ebd). DEC-2026-11-17-ta-r4-catalog-unique-allele-key and
  DEC-2026-11-17-run-susie-rss-unique-allele-key-guard-unfreeze appended (c6c450fc; append-only, 0 removed lines).
- Producer (e9c0d400): `ta_r4.catalog_unique_key` + rule split (`r4_catalog` route legacy only, shell unchanged;
  `r4_catalog_raw` same collect_region_variants.py command; `r4_catalog_unique`). RED 18F (ModuleNotFoundError) ->
  GREEN 18P; NC-P1 (no strip/upper) 5F, NC-P2 (CHR:POS key) 4F, NC-P3 (chr:pos above rs) 4F, NC-P4 (pandas
  re-serialise) 4F; module restored sha256-identical each time. Baseline suites (QUICK + in_job_gate + armed_e2e):
  per-id identical, +18 additions only (719P/2S + 26P -> 737P/2S + 26P).
- Guard (13b0821c) + re-pin (3f4d0cb9, `R_CODE_REF` 1f77128 -> 13b0821; K3 refs unchanged): RED 7F/1P; GREEN 90 ids;
  NC-G1 (guard after cap) 1F, NC-G2 (silent dedup) 2F, NC-G3 (flag dropped from argv) 1F, NC-G4 (default true) 1F;
  restored sha256-identical. Pins RED 2F/37P -> GREEN 39P. Spec update: test_json_cs_equals_fit_sets pre_fix_argv also
  strips the new flag. Pre-existing frozen-script suites (test_ld_read_path, test_finemap_receipt_early_exit,
  test_qtl_coloc_allele_join, test_no_silent_identity, test_simulation_harness): 165P/1S at e9c0d400 (shared clone)
  and at HEAD, per-id identical.
- Backup (Slurm 1960208): old_variants_r4 31, 4 panel dirs 60 rds, UKB native stats 30, AFR work dirs 70+70, each
  copy's SHA256SUMS verified against the live origin; pre_panels.sha256 (90) == backup sums; pre_untouched.sha256 203.
- Dry-run: r4_catalog_raw 31, r4_catalog_unique 31, r4_panel_afr_1kg 20, r4_identity_payload_afr 10,
  r4_panel_ukb_native 30 = 122; 0 jobs and empty --list-code-changes / --list-params-changes for the 12 legacy
  catalogs, 22 repro_routeC panels and 24 k2d targets. Fire: 122 of 122 steps, Slurm 1960869..1961081 (122 jobs,
  all COMPLETED 0:0); a following dry-run over all 179 targets (controls included): "Nothing to be done".
- Identity (Slurm 1961192): (a) raw sha256 == old pins 31/31. (b) kept + dropped == raw multiset 31/31; key sets
  equal 31/31. (c) raw 877,756; dropped exact 248,251 + case_ws 6 = 248,257; kept 629,499 = 877,756 - 248,257;
  groups 248,239 pairs + 9 triples = 248,248 groups, extra rows 248,239 + 2 x 9 = 248,257; byte-exact key extra
  248,251, normalized 248,257; SNP_ID forms {chr:pos, rs} 248,234 / {chr:pos, rs, rs} 9 / {rs, rs} 5 (sum 248,248);
  kept row not the first occurrence in 234,677 of 248,248 groups; 0 normalized duplicates in any kept catalog;
  CHR:POS extra 294,400 raw -> 46,143 kept at 46,132 sites; 30 of 31 catalogs had duplicates, BMI_Xq24 kept ==
  raw bytes; empty SNP_ID 14,799 (0 in a duplicate group); whitespace cells 0; lowercase-allele rows 17. Every
  component equals the planning measurement. (d) 90/90 panel .rds + UKB native stats byte-identical. (e) 203/203
  untouched files clean.
- Re-pin (30b13692): catalogs_sha256.tsv 30 r4 rows changed (BMI_Xq24 unchanged), 0 legacy rows. catalogs_r4_unique_key.tsv
  written (31 regions; totals == (c)). No panel manifest changed. test_live_pins: RED (Slurm 1961205) 2F/35P
  (30 of 43 catalogs fail verification; unique-key manifest absent) -> GREEN 99P. NC-L1 (uniqueness test at
  old_variants_r4) 30F/1P; NC-L2 (one multi-allelic row, FTO_16q12 16:53800387 G/A rs12446228, dropped from a tmp
  copy) fails both kept+dropped==raw and key-set == raw key set.
- Residual-risk measurement (Slurm 1961203, 9 min; script `data/r4/tmp/w3f/dupkey/measure_m123.R`, not committed).
  This still approximates `ld_allele_join_indices` (4-key or swapped-allele panel match, palindromic SNVs dropped);
  it is not the R function itself. Validation on old_variants_r4: restricted rows == measured n_variants 83/83 and
  distinct == n_variants_distinct 83/83. 815 production fits (A3_1kg, A2_identity, A3_1kg_isect, A3_ukb, A3_ukb_isect
  145 each; AFR661_A3, AFR661_A2, AFR504_A3 30 each).
  - Post-restriction 4-key duplicates: old catalogs 1,167,258 extra rows in 815/815 fits; rebuilt catalogs 0 in 0/815.
  - M1 (sumstats 4-key duplicates per window): 0 of 175 windows.
  - M2 (duplicated CHR:POS in the fit subset, the run_coloc_pair_r4.R:440 key): 3 of 815 fits, 1 extra row each,
    all A3_ukb asthma.EUR. Panel level: EUR_ukb337k_r4 34 sites in 14 of the 29 measured regions; every 1kg,
    identity and isect panel 0. Checker cross-check (`multi.pkl`): 38 sites in 15 regions = my 34 in 14 + HLA_6p21
    4 sites (HLA has no admissible fit, so it is not in the run list). The plan text's "18 regions" disagrees with the
    checker's own artifact (15). Of the checker's 6 asthma.EUR both-allele sites, 3 reach the fit subset; at
    BMI_5q13_3 75952721 (T/A), NC_SLC24A5 48303816 (G/C) and SLC2A9_urate 10203217 (A/T) one allele is a
    palindromic SNV that the allele-aware panel join drops.
  - FLAG FOR CARTER (Rule 4): M2 A3_ukb asthma.EUR MC4R_18q21 n=1 keys=18:56541713
  - FLAG FOR CARTER (Rule 4): M2 A3_ukb asthma.EUR PYHIN1_1q23 n=1 keys=1:160680184
  - FLAG FOR CARTER (Rule 4): M2 A3_ukb asthma.EUR NC_NULL_06 n=1 keys=6:81514622
    DRAFT Pre-Paste OPEN row added (gates W4a-T3); test_amendment_text 21P/2S.
  - M3 (QTL-bridge overlap of approximated fit names with the bound catalog_snp_id / catalog_chrpos spaces, old ->
    new): max per space unchanged (snp_id 19,159 -> 19,159; chrpos set 941 -> 941; chrpos bridge 207 -> 940). The
    best-space overlap fell in 39 of 815 fits (sum 1,529,761 -> 1,525,405, -4,356): A3_ukb t2d 29 fits (-4,316,
    max -735), asthma NC_ABO / NC_TYR in 5 EUR arms x 2 (-8 each arm, max -7). It rose in 0. Two causes, measured
    (probe data/r4/tmp/w3f/dupkey/m3_probe.R): (i) mixed-form fit names. A3_ukb t2d 9p21_CDKN2A has 9,609 names = 498 chr:pos +
    9,111 rs; the old snp_id space matched 498 + 7,353 = 7,851, the new one 87 + 7,353 = 7,440, and the chr:pos space
    matches only the 498 chr:pos names, so no single space now holds both forms. The "chr:pos is always recoverable"
    premise of the rsid preference holds per variant but not per space for mixed-form fits. (ii) multi-rsid groups:
    the 14 dropped rows whose SNP_ID is an rsid replaced by a smaller rsid (NC_ABO 8, NC_TYR 1); asthma NC_ABO names
    are all rsids and 7 of them are the dropped, larger rsid (233 -> 226 on A3_ukb).
  - FLAG FOR CARTER (M3): bridged overlap decreases in 39 fits (A3_ukb t2d 29; asthma NC_ABO/NC_TYR 10);
    `data/r4/tmp/w3f/dupkey/m3_decreased.tsv`. Not a Rule-4 gate under the plan; recorded for the QTL layer (W6).
- Out of scope, for Carter: (1) the 11 non-duplicate lowercase-allele rows in the r4 catalogs (17 lowercase rows
  minus the 6 case twins) are probably excluded from the UKB native panels by the case-sensitive `_allele_keys`;
  (2) the legacy catalogs (`variants_legacy`) keep 29,363 normalized duplicate rows (planning measurement), read by
  Track B allele-aware fits; both unchanged here (D-15).
- Wave close (no push). QUICK (Slurm 1961268): 738P/2S, 173.4 s wall (over 120 s; carried to 15.6). PINS 39P.
  HEAVY 244P/5S in 1,897 s. FULL (Slurm 1961269, 2,937 s): 2,463 ids = 2,408P + 53S + 2F vs the W4a baseline
  (full_W4a.xml, 2,069 ids = 2,017P + 52S): 400 added (all tests/ta_r4), 6 removed, 2 outcome changes, both tests/m3.
  - The 6 removed ids (test_coloc_pair_r4::test_panel_rsid_override_is_refused_not_dropped,
    test_contrast_stats::test_category_edges[kw11..kw14], test_run_aggregation::test_draft_writes_exactly_17_draft_tables)
    are already absent at e9c0d400, before any 15.5a test or code change; they left between W4a and 15.5 (FULL was not
    run in 15.1-15.5).
  - The 2 tests/m3 failures (test_variant_catalog_fallback_legacy_semantics::
    test_the_five_must_not_move_sites_are_byte_identical[too_many_variants_payload] and
    ::test_the_symbol_scoped_diff_is_exactly_one_removed_line) are PRE-EXISTING: 11P at 6c6e9546^ (4a1b9d4a), 2F/9P at
    6c6e9546 (15.1 N1 cap move), at 1f771281, and at e9c0d400 (pre-guard), with the same assertion text at HEAD.
    They pin the too_many_variants payload byte-identical to dc4bbd2, which the authorized N1 cap move changed.
    Not fixed here (out of scope; logged in deferred-items.md). FLAG FOR CARTER / 15.6: re-scope that pin under
    DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze.
  - A test-run side effect (tests/m3/sparse_parent_benchmark.tsv timings) was restored to HEAD, not committed.
- 15.5 PLAN frontmatter: depends_on + 2026-11-17 note already committed in 79ff8dc2 (nothing to commit).
- Handoff: 15.5 resumes: re-measure on the rebuilt catalogs, eligibility manifest, DRAFT (k) clause + the dup-key
  Pre-Paste OPEN row resolved + (c)/(m) for the 15.5a commits, 15.5 Task 3, SUMMARY; any M1/M2 OPEN row stays open
  until Carter decides and gates W4a-T3. Nothing pushed. Backups kept in `data/r4/tmp/w3f/dupkey/` until the 15.5
  remainder closes.

## 2026-11-18 — W3f 15.5 remainder (re-measure on the rebuilt catalogs; eligibility manifest; DRAFT (k); no push)

- Run list re-planned from current code into `data/r4/tmp/w3f/elig_20261118/meas` (fresh dir): 83 tasks, the same 83
  keys as 1946095; the only argv change is `--require-unique-allele-key true` (15.5a fit_command).
- Slurm 1968979 (cascadelake, 1 h, 32G): 83/83 COMPLETED 0:0, max RSS 6.7 GB; 83 JSON + RDS + inputs records.
  summarise() accepted all 83 (exact run list, early exits, no lbf_variable). Input sha256 == current pins 83/83.
  `find -L data/r4/results -newer data/r4/tmp/w3f/elig_20261118/meas/run.sh -type f | wc -l` = 0.
- eligibility_table() passes the bound check (n_variants <= panel n_var 83/83). Official
  `$MAN/w3f_fit_eligibility.tsv`: 815 rows (5 EUR arms x 145 + 3 AFR arms x 30) = 83 measured + 732 bound; not eligible 10.
- Reconciliation (`reconcile.py`, inline and Slurm 1970719, identical output), each 83 of 83:
  new n_variants == 15.5a m123_fits.tsv[new].restricted_rows; new n_variants_pre_ld == m123[new].joined_rows;
  m123[new].restricted_4key_extra == 0; new n_variants == 11-16 n_variants_distinct; new n_variants_pre_ld == 11-16
  n_pre_ld_distinct; old n_variants == m123[old].restricted_rows; old - new n_variants == m123[old].restricted_4key_extra.
- Post-restriction > 16,000, old catalogs (1946095) -> rebuilt (1968979) [m123 new]: A3_1kg 4 -> 0 [0] of 50;
  A3_ukb 6 -> 4 [4] of 15 measured (asthma, t2d x BMI_5q13_3, PYHIN1_1q23); AFR661_A3, AFR661_A2, AFR504_A3 4 -> 2 [2]
  of 6 each (asthma x BMI_5q13_3, PYHIN1_1q23). Total 22 -> 10 = 4 + 3 x 2.
- Pair rows hit: A3_1kg / A2_identity primary 0 of 100 (A2 by the bound, max identity panel 15,236); A3_ukb 14 of 100
  primary = 2 regions x (10 - C(3,2)); each AFR arm 4 of 30 = 2 regions x 2 asthma pairs; negative-control rows 0.
- Pre-fix recount (pre-LD rows > 16,000), rebuilt catalogs: 11 A3_1kg fits -> 39 primary rows = 5 regions x 7 +
  CXADR_F2RL1_6p21 1 trait x 4 (= the 11-16 "duplicates removed" figure; 12 -> 42 on the old catalogs; review 10 -> 35
  on earlier inputs).
- Regression keys A3_1kg PYHIN1_1q23: asthma n_variants_pre_ld 40,649 (> 16,000), n_variants 12,605 <= panel 15,236
  (old catalogs 22,038); t2d 36,582 / 12,584 (old 21,999).
- Proxy unchanged (repro fits, not catalog-dependent; c3e42237). confirmatory_sha256 recomputed:
  9fa410aa411fc2c682a4886dd25ca98d5dfd37f6968ecffc1a0a8860003888d5 (== 15.3 interim; old f6e6e90f…e9e3). LOCKED_PATHS 29.
- DRAFT: (k) measured-count clause; (c) one catalog row per allele key + fit refuses a repeated key; (m) + e9c0d400,
  13b0821c, 30b13692; Pre-Paste measured-count row rewritten (1968979), duplicate-key OPEN row -> RESOLVED (15.5a commits),
  analysis-code row + 15.5a; M2 CHR:POS row stays OPEN with a pointer to 15.5b (Carter a1). test_amendment_text 21P/2S.
  Extract 4,127 words (3,998 at 37b0e9e2; target ~3,100). CARTER-LOCK early-exit 0, fit-name 0, total placeholders 9.
- Wave close (no push). QUICK (Slurm 1970722): 738P/2S, 173.0 s pytest / 192.0 s wall (over 120 s; carried to 15.6).
  PINS 39P. HEAVY 244P/5S, 1,551 s. FULL (Slurm 1970723, 2,673 s): 2,463 ids = 2,408P + 53S + 2F, per-id identical to
  the 15.5a FULL (`dupkey/full_15_5a.xml`): 0 removed, 0 added, 0 outcome changes; HEAVY likewise vs heavy_15_5a.xml.
  The 2 failures are the deferred tests/m3 test_variant_catalog_fallback_legacy_semantics pair (since 6c6e9546;
  deferred-items.md, 15.6); not fixed. tests/m3/sparse_parent_benchmark.tsv timing rewrite restored to HEAD.
- OPEN after 15.5: the M2 CHR:POS row (3 A3_ukb asthma fits) -> plan 15.5b (Carter a1), gates W4a-T3. A3_ukb counts
  above (4 fits / 14 rows) are on the current UKB panels; 15.5b rebuilds them and re-measures A3_ukb eligibility.
- Push: done by the orchestrator with bb084f24 (Carter approved 2026-11-18 18:22).

## 2026-11-18 — W3f 15.5b (UKB native panels: one variant per CHR:POS, Carter a1; rebuild + re-pin; A3_ukb re-measured; no push)

Executed 2026-11-19. DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1 (5ca20376).
- Rule (after build_native's catalog filter): at a CHR:POS with 2+ variants, keep the single ACGT SNV, else drop all;
  lone variants (indels too) kept. Module `ta_r4.ukb_native_multiallelic`; `r4_panel_ukb_native` calls it;
  ukb337k_tiles.py and r4_panel_ukb_isect unchanged (526fd5c7). RED → GREEN (T-f RED 1986099, GREEN 1986169);
  NC-1..NC-8 each observed failing (NC-2 on T-f: 1986252).
- Control dry-run 1986341 (324 targets): r4_panel_ukb_native 30, nothing else. Code and params listings over the 264
  non-native targets are empty (the same filter prints the native rds: 1986415). Forcerun isect lists 29.
- Backup 1986444 (30 + 30 verified; pre_untouched 359 files); restore.sh verify 1986510 OK. Manifest recipe reproduced
  the committed bytes (1986511). Recount of the live panels before the fire (1986512) equals the planning table in every
  component.
- Fire 1986672..1986701: 30 of 30, COMPLETED 0:0. Post-fire dry-run 1987086: Nothing to be done (sidecars included).
- Identity 1987087: R_new == R_old[keep][:, keep] exactly 30/30. Variants = old − dropped, same order, 30/30.
  0 duplicated CHR:POS. n_var 189,945 − 45 = 189,900. Dropped 45 = 31 + 2 × 7. Indels 17,116 → 17,071. 15 changed +
  15 unchanged. Audit 76 = 31 kept_snv + 45 dropped. pre_untouched 359/359.
  Per region (one_snv/no_snv → dropped): 9p21 2/1→4, APOE 4/1→6, BMI 4/0→4, CXADR 3/0→3, HLA 1/3→7, MC4R 1/0→1,
  NC_NULL_01 0/1→2, NC_NULL_04/08, NC_OCA2_HERC2, NC_SLC24A5 1/0→1 each, NC_NULL_06/07 2/0→2 each, PYHIN1 6/1→8,
  SLC2A9 2/0→2. Sums: 31 + 7 = 38 positions; 31 + 14 = 45.
- Re-pin 3c1ed352: panels_EUR_ukb337k_r4.tsv 15 rows + 4 columns; n_pairs_zero_filled re-derived (BMI −16,119;
  HLA −126,457; PYHIN1 −36,398); ukb_native_multiallelic_resolved.tsv 76 rows. Live pins: RED 1987088 (15 of 30), NC-L1
  15 fail / 15 pass + PYHIN1 fail (1987388), LIVE 30/30 (1987562), NC-L2 1 fail (1987562). Verify 1987641: 280 passed.
- M2 (measure_m123.R unchanged, 1987089): A3_ukb 0 of 145, 0 of 815 overall. 1,340 non-A3_ukb rows identical to 15.5a.
  Validation non-A3_ukb 68/68; A3_ukb 9/15 vs the old-panel counts (the 6 others lost dropped variants) and 15/15 vs
  the 15.5b measurement. A3_ukb M3 (new catalogs): restricted_rows −37 over 22 fits; ov_snp_id −14 over 10 fits;
  ov_chrpos_set −3 / bridge −2; nothing rose.
- A3_ukb eligibility (1987407, 15/15 COMPLETED, no fit): A3_ukb 145 = 15 measured + 130 bound, not eligible 4 → 4.
  Table 815 = 83 + 732, not eligible 10. 70 A3_ukb lines changed; the 670 other lines are byte-identical. asthma ×
  PYHIN1_1q23 22,083 → 22,080 (07dae0c0).
- DRAFT (07dae0c0): panel sizes 35,673 / 27,268 / 25,156 / 17,980; M2 row RESOLVED; (c) disclosure (31 positions,
  7 positions / 14 variants removed, 17,071 indels kept); (m) + 526fd5c7, 3c1ed352. (k) unchanged (4 of 145).
  confirmatory_sha256 9fa410aa…88d5 unchanged. test_amendment_text 21P/2S. Extract 4,127 → 4,208 words.
- Wave close (no push): QUICK 1987855 748P/2S (171.5 s wall); PINS 39P; HEAVY 306P/5S (1,962 s; vs 15.5: +62, 0 removed, 0 outcome changes); FULL 1987856 2,535 = 2,480P/53S/2F (vs 15.5 full_15_5.xml: +72 tests/ta_r4, 0 removed, 0 outcome changes; 2F = deferred legacy_semantics pair). sparse_parent_benchmark.tsv restored.
- Not pushed. Backups stay in `data/r4/tmp/w3f/ukbbi/old/` until 15.6.

## 2026-11-19 — W3f 15.5c (tests/m3 K-1 pins ignore leading whitespace after the N1 re-indent; the one N1 emit line allowed; 15.6 FULL scope for the W4a renames; no push)

Executed 2026-11-19. DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation (fb08a75f; Carter Q1 "Ignore
indentation (Recommended)", Q3 "A: Allow the one N1 emit line (Recommended)"; both replies quoted with cat, cmp OK).
- Gate: start HEAD 61201774, origin..HEAD 0; reply sha256 55d716a4…da61d / 19c38aaf…4f12 match (replies.sha256);
  Q3 = A line grep 1. Re-measure: module 2 F / 9 P; symbol-scoped (hunk header, raw line) set == the plan's 4 pairs;
  emit lines 2 (dc4bbd2) -> 3 (HEAD); TOO_MANY_ANCHOR 1/1; default payload 17/17 lines, lstrip-equal, raw unequal,
  0 trailing ws, no "after LD" / cap_stage.
- RED (byte-exact / never-cancel / old removed+added stubs): 7 F / 24 P = the 2 original tests + #2, #8, #9, #14, #16;
  each failure at the stub predicate (lines 358, 415). #1, #17, #20 green under the stub as expected; NCs #3-7, #10-13,
  #15, #18, #19 green (raise as intended).
- GREEN dc15a630 (test file only): 31/31; collect-only id list == 11 old + the 20 in <new_tests>.
- NCs (in memory; on-disk file unchanged each time), observed failure under GREEN:
  NC-I1 value/reordered/interior_ws/trailing_ws "differs from dc4bbd2 at line 10/5/1/2 beyond leading whitespace";
  dropped "has 16 lines, dc4bbd2 has 17". NC-I2 mixed/plus4 green (each != old and != head). NC-I3 init_pair /
  path1_block / no_variants_payload / success_payload each "no longer byte-identical" (+2 indent). NC-I4 and
  NC-I8[interior] "removed something other than exactly the one authorized line"; NC-I7 "ADDED a code line other than
  the one N1 emit line". Parity: git and difflib both removed [variant_catalog_fallback <- TRUE], added [the emit],
  n_reindented 1/1. NC-I5 n_reindented 2 = 1 + 1, predicate green. NC-I6 (cancel off) n 0, emit in removed, removed
  != [K-1 line]. NC-I8[cross_hunk] n 0, both lines kept.
- No-weakening: AST of 31 of 34 pre-existing top-level nodes equal (excluded: module docstring + the two rewired tests,
  both present); PRE_K1_REF "dc4bbd2"; git diff HEAD -- src/ empty; tests/ porcelain = the one file.
- FULL Slurm 1990243 (close_c.sh, 48G, -t 03:00:00): 2,502 passed, 53 skipped in 4,657 s (wall 4,663 s, 1:17:45),
  exit 0:0. sparse_parent_benchmark.tsv restored.
  - vs full_15_5b.xml (check_15_5b.py PASS): 2,535 − 0 removed + 20 added = 2,555; added = the 20 tests/m3 ids, all
    passed; outcome changes 2 = the deferred pair failed -> passed; 2,480 + 2 + 20 = 2,502 P, 53 S, 0 F; 311/311
    HEAVY ids (heavy_15_5b.xml) present.
  - vs full_W4a.xml (check_W4a.py PASS): 2,069 − 6 + 492 = 2,555 (added 472 tests/ta_r4 + 20 tests/m3); removed = the 6
    renames, each successor present + passed: refused_not_dropped -> maps_through_panel_not_dropped (7a3415df);
    exactly_17 -> exactly_19 (ade4e9c5, bed315d4); category_edges kw11..kw14 kappa_ok -> kw12..kw15 (92caa306,
    [kw11-mcnemar-ns] present). tests/m3 1,299 (1,265 P / 34 S) -> 1,319 (1,285 P / 34 S): +20, 0 removed, 0 outcome
    changes on common ids. Confirmed by git log -S (rename_commits.txt).
  - Both checkers observed RED in memory against the wrong substrate (full_15_5b.xml as the new run): exit 1 each.
- 15.5c §C exceptions, authorized by the DEC: 2 tests/m3 outcome changes (failed -> passed); 20 new tests/m3 ids;
  QUICK and HEAVY not run separately (no src/ or tests/ta_r4 file changed; FULL contains every HEAVY id, checked);
  PINS (test_source_freeze_pins.py) ran inside FULL.
- deferred-items.md: both 2026-11-18 items RESOLVED. PLAN-INDEX: 15.5c row.
- 15.6 PLAN scoped edit (depends_on + the two allowances; 5 lines):

```diff
diff --git a/.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-PLAN.md b/.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-PLAN.md
index c517ffb7..a0ffd52e 100644
--- a/.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-PLAN.md
+++ b/.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-PLAN.md
@@ -7 +7 @@ wave: 15.6
-depends_on: ["ta-r4-W3f-eligibility-measurement-and-draft", "ta-r4-W3f-ukb-panels-biallelic"]
+depends_on: ["ta-r4-W3f-eligibility-measurement-and-draft", "ta-r4-W3f-ukb-panels-biallelic", "ta-r4-W3f-trackb-pins-indent"]
@@ -26 +26 @@ must_haves:
-    - "The FULL suite ran under Slurm and is reconciled by test id against data/r4/tmp/w4a/full_W4a.xml (2069 / 2017 / 52 / 0): 0 removed ids, 0 outcome changes in tests/m3, every added skip or fail explained by id; any failure is a STOP"
+    - "The FULL suite ran under Slurm and is reconciled by test id against data/r4/tmp/w4a/full_W4a.xml (2069 / 2017 / 52 / 0): 0 removed ids except exactly the 6 W4a ids in deferred-items.md's rename map, each with its named successor present, 0 outcome changes in tests/m3 on common ids; tests/m3 additions only the 20 15.5c ids (DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation), every added skip or fail explained by id; any failure is a STOP"
@@ -130 +130 @@ STATE.md: the "## 2026-11-04 — TRACK A ta-r4: W4a Tasks 1–2 COMPLETE ... (
-       line; added outcomes and modules; tests/m3 before → after. Required: removed 0; tests/m3 outcomes unchanged; 0
+       line; added outcomes and modules; tests/m3 before → after. Required: removed 0 except exactly the 6 W4a ids in deferred-items.md's rename map, each with its named successor present; tests/m3 outcomes unchanged on common ids; tests/m3 additions only the 20 15.5c ids (DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation; see deferred-items.md); 0
@@ -142,2 +142,2 @@ STATE.md: the "## 2026-11-04 — TRACK A ta-r4: W4a Tasks 1–2 COMPLETE ... (
-    - reconcile_W3f.txt shows removed 0, changed limited to listed spec updates (ids pasted), failed 0, and an arithmetic line base − removed + added = new that holds
-    - tests/m3 outcome Counter identical before and after
+    - reconcile_W3f.txt shows removed 0 except exactly the 6 W4a ids in deferred-items.md's rename map, each with its named successor present (see deferred-items.md), changed limited to listed spec updates (ids pasted), failed 0, and an arithmetic line base − removed + added = new that holds
+    - tests/m3 outcome Counter identical before and after on common ids; tests/m3 additions only the 20 15.5c ids (DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation) (see deferred-items.md)
```

- Not pushed.

## 2026-11-19 — W3f 15.6 wave close (brief-blind re-review; FULL reconciled; records; W4a depends_on)

- Premises re-measured at HEAD 03b60744 before acting: confirmatory_sha256 9fa410aa…88d5 (canonical_sha256 of
  decision_rules.yaml `confirmatory:`), `locked` False, n_regions_min 7, LOCKED_PATHS 29, extract 4,208 words, HANDOFF
  w4a_checkpoint untouched since W4a (confirmatory_sha256 still f6e6e90f…), W4a plan 0-line diff vs 72b99064.
- Review: prompt `data/r4/tmp/w3f/codex_prompt.md` = the W4a wrapper bytes with the new extract (sha256 6bce3707…7339);
  codex-cli 0.166.0 (W4a scratch prefix), `-m gpt-6.1-sol`, rc 0 first attempt, 12m46s; output 35,587 B sha256 e66f3c96…;
  banked block byte-equal to raw stdout. 23 findings = 23 rows: DRAFT fixed 6 (F5, F13, F14, F16, Q4, Q6; 7 replacements,
  `data/r4/tmp/w3f/draft_fix.py`), OPEN for Carter 11 code (F1–F4, F6–F12) + 1 disclosure (F15), optional 1 (Q2), rejected 1
  (Q1), noted 3 (Q3, Q5, Q7). F16 verified by fetching PLoS Genet e1012155 (2026-05-19; `data/r4/tmp/w3f/ext/`, sha256
  edfdc74a…). test_amendment_text 21 P / 2 S; NC ("pivot" in the extract) → test_draft_extract_framing FAILED, restored.
  Extract 4,283 words. Commit 5a6d4a01.
- §C close Slurm 1992683 (c025n04, HEAD 5a6d4a01, `close_W3f.sh` = close_W4a.sh + junitxml path + RSCRIPT export; --mem 48G
  as 15.5c, seff 48.00 GB = 100%): QUICK 748 P / 2 S in 150.7 s (over 120 s, as 15.5b); HEAVY 306 P / 5 S (4 W5a/W5b skips +
  asthma.AFR grch38_backup no tabix index); PINS 39 P; FULL 2,555 = 2,502 P / 53 S / 0 F (47m10s).
- Reconciliation (`data/r4/tmp/w3f/reconcile_W3f.txt`, `check_W3f.py`): vs full_W4a.xml base 2069 (2017/52) → 2555
  (2502/53); common 2063, removed 6 (= the deferred-items rename map, each successor passed), added 492 (ta_r4 472, m3 20;
  491 P + 1 S), changed 0; 2069 − 6 + 492 = 2555; tests/m3 1299 (1265/34) → 1319 (1285/34), common unchanged, added = the 20
  15.5c ids, all passed. Only new skip: test_sumstats_build::test_provenance_inputs_measured_build_equals_declared
  [sumstats_asthma_AFR-lifted_from] (no tabix index; skipped in 15.5c too). vs full_15_5c.xml: 0 removed / 0 added / 0
  changed. `indent/check_W4a.py` pointed at full_W3f.xml (`check_W4a_on_W3f.py`, one-line path change): PASS. Negative
  controls: check_W3f on full_15_5b.xml FAIL (6 MISS); on a synthetic XML (one ta_r4 id removed, one m3 id failed) FAIL.
  sparse_parent_benchmark.tsv porcelain empty.
- HANDOFF.json: N1/N2 + 10 other_code_items RESOLVED with commits (originals under `*_PRE_2026_11_04`); W3f_F1–F12, F15
  added as production_blockers, W3f_optional under other_code_items; proposed_lock_values confirmatory_sha256 9fa410aa…
  (old under confirmatory_sha256_PRE_W3f), n_regions_min, confirmatory_direction_test, region_contribution_proxy (+ FLAGs);
  resume_on_reconnect annotated; suite_baselines_ta_r4_latest → FULL 2555/2502/53/0 (W4a string kept as
  suite_baselines_ta_r4_W4a); do_not run_susie_rss.R annotated with both lifts (N1 and 15.5a guard — the plan's "N1 only"
  text predates 15.5a); read_first + the review file. Keys 330 → 359 (all pre-existing strings still contained).
- PLAN-INDEX: dated notes on §B.6 (two lifts; R_CODE_REF 13b0821) and §B.8 (Slurm); 15.5 row push fact; 15.6 row.
  W4a plan: depends_on → ["ta-r4-W3f-review-suite-and-close"] (1 line vs 72b99064; tasks untouched).
- No production fit, no locked: true, no signoff, no OSF. Push WITHHELD (orchestrator to ask Carter).

## 2026-11-20 — W3f 15.7a (review F1: runtime config guard; opens 15.7; no push)

- Commit 1 c015a4e4: the 15.6 reply, 12 Carter 15.7 replies, F15 wording v1 + v2 (15 files, sha256 in
  `data/r4/tmp/w3f/q157/replies.sha256`, also quoted in the DEC), the eleven 15.7 PLAN files, PLAN-INDEX, and
  DEC-2026-11-20-ta-r4-w3f-15-7-code-fixup (each file quoted via cat; extracted and byte-compared 15/15; NC with one
  changed byte → DIFF).
- Reply gate `$Q/gate_reply.py`: 14 NCs (a)–(n) in `$Q/gate_nc.txt`, each with the expected rc and its own named
  reason (12 → 2; (l), (m) → 0; (k) with both files present → 0); the 12 real reply files → 0 (`$Q/gate_real.txt`;
  Q-PROXYA / Q-PROXYB question read from the file's line 1). `$Q/close.sh` (= close_W3f.sh + junit path + header),
  `$Q/check_tmpl.py`.
- Measured (`$Q/smk_attrs.txt`, c020n03): `config_args` None / ['x=1']; `overwrite_configfiles` = command-line list,
  absolute, in order; `configfiles` = that + the directive's relative `config/pipeline.yaml`. As planned.
- RED (`$Q/red_15_7a.txt`): 31 F / 18 P exactly as listed (2–6, 8–13, 15–22, 29–32 + the 8 gate-shell spec updates
  red; 1, 7, 14, 23–28 + the 4 fire spec updates green), each for the stub/unchanged-code reason.
- GREEN commit 2 420aa998: `ta_r4/job_guard.py`; `gate_command(stage, arm, config, label)` + `commands.job_label`;
  5 call sites; Snakefile.ta_r4 parse-time refusal; r4_fire.sh env refusal + allowlist; DRAFT (k) clause.
  Task 1 verify (sbatch, c020n03 Gold 6226R): 197 P / 2 S; test_job_guard collects 32; ids vs full_W3f.xml 0 removed,
  0 changes, +32 passed (test_slurm_profile 15 and test_qtl_group_runner 24 identical). Mutation NCs
  (`$Q/mutation_nc_15_7a.py`): constant digest, no lock gate, no record, bf16 unchecked, OpenBLAS unchecked, set (not
  ordered) configfile compare → each failed exactly its named tests; files restored byte-for-byte. Non-weakening AST
  PASS (only _fire_repo, _fire and the two named tests; NC FAIL). test_amendment_text 21 P / 2 S.
- FULL Slurm 2007035 (c020n03, HEAD 420aa998): QUICK 775 P / 2 S; HEAVY 311 P / 5 S; PINS 39 P; FULL 2,587 = 2,534 P /
  53 S / 0 F. `check_15_7a.py` PASS vs full_W3f.xml (0 removed, +32, 0 changes, 12 declared passed → passed); NCs
  (baseline as new; synthetic failed id) FAIL.
- srun under QOS normal is refused interactively → every verify ran with `sbatch --wait` on the same
  partition/account/QOS/constraint. A foreign docs commit 61994a1b (HANDOFF/.continue-here) landed during FULL.
- No push, no production fit, decision_rules.yaml locked: false, no OSF, n_regions_min 7.

## 2026-11-20 — W3f 15.7b (review F4 F6 F7: completeness by identity; no push)

- Start 6ff8c0de (`$Q/start_15_7b.txt`). Re-measured (`$Q/measure_15_7b.txt`): stable_index source as planned; yaml 10×5×2 =
  100 cells, reps 200, seed_base 20261021; qtl_manifest.tsv 116,551 lines, 0 duplicate qtl_row_id; callers as planned.
- RED Task 1 (`$Q/red_15_7b_t1.txt`, stubs reconcile → ok, stable_index → 0, _sim / _qtl_missing unchanged): 20 F / 4 P
  exactly as planned (green 1, 5, 14a, 15). 14b failed on ImportError; its NC against the start parser
  (`$Q/nc_header_parser_15_7b.txt`) FAILs: region / scenario / gen_panel / reps / config_sha256 lost.
- GREEN: id_reconcile; _sim identity (sim_header, _sim_identity); _qtl_coverage (replaces _qtl_missing, no other caller);
  tierable_summary(manifest=None) + `--manifest` without default; smk appends `--manifest {input.manifest}`. Fixture
  builders build_tree / final_repo (+ _write_sim, QTL_IDS) and _cell / sim_repo (+ _sim_cfg, _seed). Task 1 verify 82 P;
  test_in_job_gate + test_confirmatory_completeness + test_job_guard 60 P, 0 changes vs full_15_7a.
- AST no-weaken (`$Q/noweaken_15_7b.txt`) PASS: only the four fixture helpers changed, helpers/constants/hashlib added,
  no test_* changed, order kept. NC (one weakened assertion) FAIL (`$Q/noweaken_15_7b_nc.txt`).
- RED Task 2 (`$Q/red_15_7b_t2.txt`): 6 F / 1 P as planned (27 green). GREEN run_row `_empty_reason`; 7 P.
- Mutation NCs (`$Q/mutation_nc_15_7b.txt`, 10 mutations, source md5-restored): each failed its enforcers. Run 1
  (`$Q/mutation_nc_15_7b_run1_mispredicted.txt`) had two wrong predictions, not code defects: M1 (duplicates ignored)
  leaves copies_of_rep1 refused by the missing ids 2..reps; M4 `if False:` left the elif mismatch branch live, so it was
  split M4a / M4b (M4a's missing-token case fails by KeyError, M4b's mismatch case by not raising).
- DRAFT (l) one sentence (`$Q/draft_15_7b.py`); (g) "exactly the configured 200 replicates per arm" matches, unchanged.
  test_amendment_text 21 P / 2 S. Commit 5fce26a8.
- FULL Slurm 2008417 (sbatch --wait, cascadelake c020n03, HEAD 5fce26a8): QUICK 804 P / 2 S; HEAVY 313 P / 5 S; PINS 39 P;
  FULL 2,618 = 2,565 P / 53 S / 0 F = 2,587 + 31. vs full_15_7a.xml: 0 removed, +31 (all passed), 0 outcome changes,
  tests/m3 0. check_15_7b.py PASS; NCs (base as new; synthetic failed pre-existing id) FAIL. Declared spec updates: none.
- No push, no production fit, decision_rules.yaml locked: false, no OSF, n_regions_min 7.

## 2026-11-20 — W3f 15.7c (review F10: cross-panel purity variant resolution; no push)

- Start 0351c628 (`$Q/start_15_7c.txt`). The real-fit route probe was re-run (Slurm 2009767, `$Q/c157/f10_real_fit_routes_rerun.tsv`) and is
  byte-identical to the planning output. Over 20 fits: 33,438 names, 14,063 suffixed. Routes: sumstats 6,282, panel 22,092,
  chrpos 0, unresolved 0, multi-key 0. Every suffixed name duplicates a single key (5,064 on the sumstats route, 8,999 on the panel route).
- Name rebuild (`$Q/c157/rebuild_names.R`, same job): an independent emulation of the run_susie_rss.R chain (sumstats
  read, window, catalog join in catalog order, allele-aware panel match, rsid override, blank → CHR:POS, make.unique)
  compared to colnames(fit$lbf_variable) with identical(): **20/20 exact**. Override 22,092 names; make.unique 14,063; blank 0.
- RED (`$Q/red_15_7c.txt`; the start script accepting the new options, variant_match.R absent): 13 F / 5 P as planned
  (green 3, 5, 8, 9, 15). Test 2's first fixture (C/T, the strand complement of A/G) was corrected to A/C. Its RED
  was re-confirmed against the start script (`$Q/c157/red_test2_refixture.txt`).
- GREEN: variant_match.R (classification moved; panel_alleles, panel_keeps, resolve_fit_names); run_coloc_pair_r4.R
  sources it from its own directory; cs_cross_purity.R takes the five new required arguments plus --allow-duplicate-rows,
  and gains the route / match-kind / n_refused_multi_key columns; run_aggregation passes the fit's sumstats, catalog,
  region id, regions csv and panel, and checks the fit JSON's catalog and panel per fit (FINAL exit 3 / DRAFT note).
  Heavy tests 10 and 18 passed (Slurm 2009922). Superset over 29 regions, both directions: 167,956 of 167,956 kept;
  no count is asserted. Task 1 verify (Slurm 2009987, sbatch --wait, cascadelake): 114 P / 2 S.
- Mutation NCs (`$Q/mutation_nc_15_7c.txt`): 9 mutations, each failing exactly its predicted tests, source md5-restored.
  Run 1 (`$Q/mutation_nc_15_7c_run1_mispredicted.txt`): M5 also fails test 5 (palindromic members resolve through the panel route);
  M9's old string had the wrong indentation, and the count assertion caught it. No-weaken AST PASS (`$Q/noweaken_15_7c.txt`); its NC FAILs.
- DRAFT (e) E4: one replacement (`$Q/draft_15_7c.py`); test_amendment_text 21 P / 2 S. Commit e1422df1.
- FULL Slurm 2010023 (cascadelake c020n03, HEAD e1422df1): QUICK 820 P / 2 S; HEAVY 315 P / 5 S; PINS 39 P; FULL
  2,636 = 2,583 P / 53 S / 0 F = 2,618 + 18. vs full_15_7b.xml: 0 removed, +18 (all passed), 0 outcome changes,
  tests/m3 0, 7 declared spec updates passed → passed. check_15_7c.py PASS; its NCs (base as new; synthetic failure on a declared id)
  FAIL.
- Deviations: a fit-panel check was added beside the catalog check (Rule 2); test 10 is marked r4_heavy; the region id
  is derived in _rscript_purity.
- No push, no production fit, decision_rules.yaml locked: false, no OSF, n_regions_min 7.

## 2026-11-20 — W3f 15.7d (review F12: A1 allvars secondary table; no push)

- Start 7b1e0fd2 (`$Q/start_15_7d.txt`), written into the test as the literal PRE_157D_REF.
- RED (`$Q/red_15_7d.txt`): tests 1-5 FAIL (table absent; family absent), test 6 PASS, as planned.
- GREEN (1cf179d1): A1_ALLVARS_EUR / A1_ALLVARS_AFR; table `a1_allvars_secondary` (20th, after afr_secondary) =
  e6_panel_contrast over the confirmatory EUR ids and the AFR ids, with an ancestry column; row_drops family
  `a1_allvars`. Declared rename test_draft_writes_exactly_19_draft_tables → _20_ (TABLES tuple gains the table);
  declared spec update test_row_drops_and_long_e6_tables (family set gains a1_allvars). Task 1 verify 59 P / 2 S.
- Mutation NCs (`$Q/mutation_nc_15_7d.txt`): 6 mutations, each failing exactly its predicted tests, source md5-restored.
  Run 1 (`$Q/mutation_nc_15_7d_run1_mispredicted.txt`): M4 also fails test_branch_outcomes_two_confirmatory_rows (it
  checks via), M5 also fails test 2 (it asserts the AFR n); predictions corrected, no code or test changed.
  No-weaken AST PASS (`$Q/noweaken_15_7d.txt`); its 5 NCs FAIL.
- DRAFT (e): one insertion after the AFR sentence (`$Q/draft_15_7d.py`); test_amendment_text green.
- FULL Slurm 2011462 (cascadelake c020n03, HEAD 1cf179d1): QUICK 826 P / 2 S; HEAVY 315 P / 5 S; PINS 39 P; FULL
  2,642 = 2,589 P / 53 S / 0 F. vs full_15_7c.xml: removed 1 (the _19_ id), +7 (6 new + _20_, all passed), 0 outcome
  changes, tests/m3 0, declared spec update passed → passed. check_15_7d.py PASS; its NCs (base as new; synthetic
  failure on the declared id) FAIL.
- No push, no production fit, decision_rules.yaml locked: false, no OSF, n_regions_min 7.

## 2026-11-20 — W3f 15.7e (review F8 F11: known-state no-CS and NC rates by method; Carter Q-DEN A; no push)

- Gate: `$Q/gate_reply.py Q-DEN` printed "A: Known states only (Recommended)" and 0775b935…b832c, rc 0 (`$Q/gate_15_7e.txt`).
- Start f20b667b (`$Q/start_15_7e.txt`) = the test literal PRE_157E_REF. DEC-2026-11-20-ta-r4-none-rows-denominators
  (699fdb23) quotes the reply file, cmp-identical.
- RED (`$Q/red_15_7e.txt`): tests 1-5, 7-11 and the declared assert FAIL; 6 and 12 PASS; test_e4_no_cs_rate and
  test_e4_no_cs_rate_levels_and_denominators PASS with their values, as measured at planning.
- GREEN (8d272492): R early-exit branch keeps the completed side's n_cs, records early_exit_a / early_exit_b (early-exit
  docs only; fitted docs' exact key set unchanged); e4_no_cs_rate n_unknown + no_cs_rate_known; negative_control_rates
  long by method + with_posterior (n_fallback_abf), none share NaN. Declared spec update
  test_row_counts_equal_fixture_admissible_rows. Task 1 verify + test_coloc_pair_r4.py, Slurm 2012646: 103 P / 2 S.
- Mutation NCs: light M1-M10 (`$Q/mutation_nc_15_7e_light.txt`) and heavy H1-H2 (Slurm 2012849) each fail exactly
  their predicted tests, source md5-restored. Heavy run 1 (Slurm 2012775) mispredicted H1 (test 2 also asserts the
  completed side's n_cs); prediction corrected, no code or test changed. No-weaken AST PASS; its 4 NCs FAIL.
- DRAFT (e) E4 pair level and (l) NC share rewritten (`$Q/draft_15_7e.py`); test_amendment_text green.
- FULL Slurm 2012884 (cascadelake c023n03, HEAD 8d272492): QUICK 836 P / 2 S; HEAVY 317 P / 5 S; PINS 39 P; FULL
  2,654 = 2,601 P / 53 S / 0 F. vs full_15_7d.xml: 0 removed, +12 (all passed), 0 outcome changes, tests/m3 0,
  declared spec update passed → passed. check_15_7e.py PASS; its NCs (base as new; synthetic failure on the declared
  id) FAIL.
- No push, no production fit, decision_rules.yaml locked: false, no OSF, n_regions_min 7.

## 2026-11-21 — W3f 15.7f (review F2: exact credible-set purity, GWAS and QTL; Carter Q-F2 A, Q-F2Q i; no push)

- Gates: `$Q/gate_reply.py Q-F2` printed "A: Exact purity, third unfreeze (Recommended)" and 57886063…c52e5a, rc 0;
  `Q-F2Q` printed "i: Same treatment on the QTL side (Recommended)" and 63a54f5f…ab790e, rc 0 (`$Q/gate_15_7f.txt`).
- Start 78f62719 (`$Q/start_15_7f.txt`) = the test literal PRE_157F_REF. DEC-2026-11-20-run-susie-rss-exact-purity-unfreeze
  and DEC-2026-11-20-ta-r4-qtl-exact-purity-flag (29de2a4d) quote the reply files, cmp-identical.
- susieR 0.14.2 `get_purity`: `if (length(pos) > n) pos = sample(pos, n)`, n = n_purity = 100; `susie_get_cs` and
  `susie_suff_stat` forward `n_purity`; coloc 5.2.3 `runsusie` forwards `...` to `susie_rss`; `annotate_susie` does not
  recompute purity.
- Flip measurement (c3c76ba2, before any code change; `$Q/purity_flip_measure.R`, Slurm 2014394 cascadelake c020n04):
  20 A3_1kg_newcat pilot fits, every panel sha256 = its manifest row, every fit variable resolved (variant_match.R,
  allow_duplicate_rows). Identity checks (i) 19/19 stored sets = alpha 95% sets, (ii) 19/19 stored purities (all
  <= 100 members) exact within 1e-12 (non_converged fits on R/(1+eps)). 109 components with V > 1e-9 and a set > 100
  in 12 fits (reconciled to planning). Exact min |r| 0..0.0243; share of seeds 1..1000 with subsample min >= 0.5 is
  0.000 for all 109; kept 0/109; demonstrated flips 0 (none of the pilot drops would change under exact purity).
  Largest set 3,350 (asthma FTO_16q12 L3); 39 of the 109 duplicate an earlier component's set. Peak RSS 14.2 GB
  (sacct MaxRSS).
- QTL memory (Slurm 2014452, c021n03; PYHIN1_1q23, 15,236 variants as the set): panel + susie_get_cs 11.1 GB with
  n_purity 100 and with n_purity all; with the run_qtl_coloc.R / runsusie / susie_rss copies live 19.3 GB, again the
  same for both (the p x p copies and the symmetry check dominate; exact purity adds nothing measurable at the cap).
  > 6 GB → `r4_qtl_group:mem_mb=30000` (ceil(19.7 GB x 1.5)), one resource line; test_slurm_profile 15 passed.
- RED (`$Q/red_15_7f.txt`, Slurm 2014603): 9 failed / 4 passed. Tests 2, 3, 5, 6, 7, 9, 12, 13 failed on the missing
  flag; 4, 8, 11 passed as planned; 10 passed (it reads the manifest committed in c3c76ba2, not the code). Test 1
  failed on its own non-vacuity check (seeds 1-3 all drew LOW); widened to the 8 seeds before GREEN.
- GREEN (57ddb59d): `--exact-purity` in run_susie_rss.R (ladder policy n_purity, sweep and L-saturation) and
  run_qtl_coloc.R (both runsusie calls); fit_command non-legacy arms, qtl_command QTL_A3 / QTL_A2, simulation ladder.
  Task 2 verify set (Slurm 2014634, pre-repin): 308 P / 2 S / 9 F, the 9 = 3 freeze pins + 1 imported R pin + 5
  working-tree-vs-HEAD guards, all resolved by the commits.
- Re-pin (38e4080d): R_CODE_REF 13b0821 → 57ddb59; pins 3 F / 36 P before, 39 P after.
- Mutation NCs (`$Q/mutation_nc_15_7f.py`, Slurm 2014781 + 2015125): M1-M11 each fail exactly their predicted tests,
  sources md5-restored. M9 run 1 (QTL default call + prior_variance 0.05) failed nothing: the prior is re-estimated and
  the JSON is unchanged (`$Q/mutation_nc_15_7f_run1_M9_weak.txt`); with prior_variance 1e-4 fixed it fails test 11.
- DRAFT (k) (b11b10b6, `$Q/draft_15_7f.py`); test_amendment_text 21 P / 2 S.
- FULL Slurm 2015198 (cascadelake c020n01, HEAD b11b10b6): QUICK 839 P / 2 S; HEAVY 327 P / 5 S; PINS 39 P; FULL
  2,667 = 2,614 P / 53 S / 0 F. vs full_15_7e.xml: 0 removed, +13 (all passed), 0 outcome changes, tests/m3 0,
  3 declared spec updates passed → passed. check_15_7f.py PASS; its NCs (base as new; synthetic failure on a declared
  id) FAIL, rc 1.
- No push, no production fit, decision_rules.yaml locked: false, no OSF, n_regions_min 7.

## 2026-11-21 — W3f 15.7g (review F3: the QTL PP.H4 sweep uses the GWAS PP.H4; NaN GWAS rule for r4; Carter Q-F3 B, Q-F3B A; no push)

- Gates: `$Q/gate_reply.py Q-F3` printed "B: Fix the sweep for Track B too" and f8694860…664703, rc 0; `Q-F3B`
  printed "A: Keep it as today, logged as the legacy rule (Recommended)" and b744a828…1cc1b, rc 0 (`$Q/gate_15_7g.txt`).
- Start 62353dbe (`$Q/start_15_7g.txt`) = the test literal PRE_157G_REF. DEC-2026-11-20-ta-r4-qtl-sweep-gwas-pph4
  (90cf52d7) quotes both replies; Track B assign_tiers sweep output changes by Carter's choice.
- Track B count: not measurable, no artifact. Read-only md5 search for 17ff46db… (Slurm 2016136; results/,
  /share/clintonlab/ckclinto, /rs1/researchers/c/ckclinto, depth 6, `*tier*`): 60 candidates, 0 hits.
- RED (`$Q/red_15_7g.txt`, Slurm 2016160): 10 failed / 1 passed. Tests 1-8, 10, 11 failed on the defect; 9 (full mode
  without the flag byte-identical to PRE_157G_REF) passed, as planned.
- GREEN (7405ba4a): sweep_tiers with a GWAS table applies the tier definitions to (best GWAS, best QTL) over the GWAS
  regions, with tier_b_min from the config; without one it is the pre-15.7g sweep, logged as the legacy rule.
  `--nan-gwas-below-threshold` (r4_qtl_tiers only, via run_qtl_group_r4.tiers_argv; `--input` order kept); NaN-GWAS
  group count logged in every mode. Declared spec update: sweep assertions of
  test_qtl_fallback_export::test_tiers_from_tierable_equal_tiers_from_full (hand derivation `$Q/spec_update_15_7g.txt`).
  Task 1 verify set (Slurm 2016337, 2016424 after the DRAFT edit): 108 P / 2 S / 0 F; Track B rules and config
  unchanged.
- Mutation NCs (`$Q/mutation_nc_15_7g.py`, Slurm 2016362): M1-M13 each fail exactly their predicted tests; phase2
  never fails; sources md5-restored.
- QTL_legacy: qtl_tiers.tsv is full mode, untouched by the sweep fix. Synthetic measurement (`$Q/qtl_legacy_tiers_15_7g.py`,
  Slurm 2016384): 200 frames, 0 violations (flag on: only NaN-GWAS rows move, 194 rows in 126 frames; flag off:
  byte-identical). Real data: 0 of 100 repro_routeL pair JSONs exist (not measurable before W6). Planning bound
  re-measured, unchanged. HANDOFF do_not W6 tripwire added (13 → 14 strings).
- NaN-rule affected groups on real r4 inputs: not measurable (0 of 100 pair JSONs per QTL arm). Logged count on the
  fixtures: 2 (full and sweep).
- DRAFT (l) sweep sentence (`$Q/draft_15_7g.py`); test_amendment_text 21 P / 2 S.
- FULL Slurm 2016509 (cascadelake c020n01, HEAD 7405ba4a): QUICK 849 P / 2 S; HEAVY 328 P / 5 S; PINS 39 P; FULL
  2,678 = 2,625 P / 53 S / 0 F. vs full_15_7f.xml: 0 removed, +11 (all passed), 0 outcome changes, tests/m3 0,
  tests/phase2 0, declared spec update passed → passed. check_15_7g.py PASS; its 3 NCs (base as new; synthetic failure
  on the declared id; on a phase2 sweep id) FAIL, rc 1.
- No push, no production fit, decision_rules.yaml locked: false, no OSF, n_regions_min 7.


## 2026-11-21 — W3f 15.7h (F9 null-window re-selection on the production inputs; Carter Q-F9 A; no push)

- Gate `$Q/gate_reply.py Q-F9` printed "A: Re-run the selection on the production inputs (Recommended)" and
  c2cc9915…cc089, rc 0. Start 63083a1d (`$Q/start_15_7h.txt`). DEC-2026-11-20-ta-r4-null-window-reselection (6fffde86).
- Driver (0e6dda24): `--sha256-manifest` also keyed by `path`. Identity on the superseded inputs (Slurm 2017268): the
  superseded selection byte for byte, candidates 352c77ec…. Production (Slurm 2017289): 2,886 candidates (a0067cc7…),
  2,745 shared / 120 dropped / 141 added; seed 20261021 keeps NC_NULL_07 11:21500001 and NC_NULL_09 13:71000001.
  Old → new: 01 1:99500001 → 1:99750001; 02 1:218750001 → 1:232000001; 03 2:190000001 → 2:202500001;
  04 3:30750001 → 3:34000001; 05 3:178250001 → 3:191500001; 06 6:81500001 → 6:82750001; 08 13:38500001 → 13:42000001;
  10 14:49000001 → 14:49250001. Superseded selection kept (sha256 f0df241a…).
- Tiles: missing = the 6 planned (`$Q/tile_feasibility.txt`); compute nodes cannot reach S3 (Slurm 2017274, curl rc 28);
  fetched on login02 with fetch_tile (6,470,831,032 bytes, 90 s); re-verified 12/12 incl. multipart ETag (Slurm 2017319);
  76 → 88 rows; the 20 other autosomal regions' tile choice unchanged.
- RED Slurm 2017257 (KeyError relative_path; test 3); test 4 RED after the re-selection; GREEN Slurm 2017268, 2017310.
  NCs NC-1/NC-2 (Slurm 2017530), NC-4, NC-5, NC-D, NC-D2, NC-L (Slurm 2020806) each failed as predicted; files restored.
- Rebuild: regions_r4.csv 8 rows; pair_manifest unchanged; `bin/r4_fire.sh repro repro_routeC` 48 jobs (Slurm
  2017707–2017862, 48/48 0:0); post-fire dry-run nothing to do. Snapshot (2017291 / 2017920): 702 of 822 files identical,
  117 changed = the 8 windows, 3 named files; NC_NULL_07/09 32/32.
- Re-pin (Slurm 2017965; 2017926 OOM at 16G, nothing written): every other row reproduced byte for byte, then the 8
  windows' rows replaced in catalogs_sha256, catalogs_r4_unique_key, the 5 EUR panel manifests and
  ukb_native_multiallelic_resolved (the 2 extra manifests per Carter 2026-11-21 Q1 "Commit them (Recommended)",
  `W3f-carter-15-7h-repin-and-draft-reply-2026-11-21.txt`). Live pins 160 P; Task 2 verify 61 P / 2 S (Slurm 2020806).
- Eligibility (Slurm 2018025): 815 = 83 measured + 732 bound, 10 not eligible (unchanged); NC_NULL 250 bound.
- DRAFT: line 42, (l) line 126; PASTE (c) line 80 (Carter Q2 a) 31 → 30, 7 / 14 → 6 / 12, 17,071 → 16,843 from
  Slurm 2021384 (the same script reproduces 31 / 7 / 14 / 17,071 on the pre-rebuild panels); line 33 unchanged.
  Commit 350cd9b9.
- FULL Slurm 2021566 (cascadelake c020n01, HEAD 350cd9b9): QUICK 851 P / 2 S; HEAVY 330 P / 5 S; PINS 39 P; FULL
  2,682 = 2,629 P / 53 S / 0 F. vs full_15_7g.xml (`junit_cmp.py`): 0 removed, +4 (all tests/ta_r4, all passed), 0
  outcome changes, tests/m3 0; declared spec update passed → passed; the 4 other selection-touching ids passed in both.
  `$Q/check_15_7h.py` CHECK PASS rc 0; its 3 NCs (base as new; synthetic failure on the declared id; on
  test_regions_r4_is_rebuilt_from_sources) each CHECK FAIL, rc 1 (`$Q/check_15_7h_nc.txt`).
- Run interrupted ~07:27 by a parent restart; resumed with Carter's approval after re-checking every uncommitted edit.
- No push, no fit, no colocalization on a null window, decision_rules.yaml locked: false, no OSF, n_regions_min 7.


## 2026-11-22 — W3f 15.7h2 (n_regions_min option D: exact-purity region-contribution proxy; 20 asthma pilot commands, asthma then excluded; Carter Q-PROXY, Q-PROXYA B, Q-PROXYB A, Q-NREG, Q-PURITY A, Q-MEMK2D, Q-DROPASTHMA; no push)

- Start 892c4443 (`$Q/start_15_7h2.txt`). Gates: gate_reply.py Q-PROXY, Q-PROXYA, Q-PROXYB, Q-NREG rc 0 (`$Q/gate_15_7h2.txt`);
  Q-PURITY (ls-files, diff, bf5185dc…f614a6, last line; `$Q/gate_15_7h2_purity.txt`); Q-MEMK2D (c2783c9b…1030c, lines 3/7;
  `$Q/gate_15_7h2_memk2d.txt`); Q-DROPASTHMA (072f5279…b402, last line; `$Q/gate_15_7h2_dropasthma.txt`); each with
  negative controls observed failing. DECs (each quoting its reply files, cat + cmp rc 0): DEC-2026-11-20-ta-r4-proxy-asthma-refit-keep-n-regions-min-7
  (d1498dff), DEC-2026-11-21-ta-r4-proxy-exact-purity-scored-matrix (f1f17bef), DEC-2026-11-21-ta-r4-proxy-k2d-identity-and-56g
  (563f4753), DEC-2026-11-22-ta-r4-proxy-drop-asthma-build-mix (688a6220).
- Input pins `$Q/proxy_asthma_inputs.tsv` (76098b25…): 39 rows match or recorded (corrected asthma 49edfc54… + .tbi, 10 legacy
  catalogs, 10 legacy_repro/EUR + 10 k2d_identity/EUR panels, run_susie_rss.R, POLICY_REPRO, regions_r4.csv, pipeline.yaml);
  tampered-pin NC rc 1. R env (from LSF 431248's snakemake argv): smk_job_envs/ta_r4/0f3436279d4146c376747a0ea5bfd4bf_,
  r-base 4.4.2 / r-susier 0.14.2 / r-coloc 5.2.3.
- Stops answered by Carter: (1) Rule-4 before any fit: non_converged repro fits keep fit3, stored purity = panel / (1+eps)
  (ratio 0.9999000100 on 6 sets of 5 EUR repro_routeC fits) → Q-PURITY A. (2) k2d cost sample over 40 GB and 22/34 k2d rows
  unmapped in the dry run (Slurm 2026120; k2d identity panels list two rows per allele key) → Q-MEMK2D (56G; identity fits skip
  mapping). (3) corrected-asthma pilot fits mix builds → Q-DROPASTHMA.
- Code 265434df (asthma_pilot_commands / _split_commands; region_contribution_proxy exact_purity / asthma_fit_root / fits_tsv /
  policy_path; CLI flags) and bcd0310a (identity iff the fit JSON records it, cross-checked against the panel); tests 4f3d692a.
  RED: 8 of 9 (test 2 green by construction; red_15_7h2.xml), then test 2 (a)/(b) on 265434df (red_15_7h2b.xml,
  g157h2/red_case_b.txt). NC-1..NC-9 each RED on its named test, restores `git diff --quiet -- src` clean, restored tests green
  (`$Q/negctl_15_7h2.txt` 533311ee…; earlier runs kept in g157h2/).
- Split Slurm 2025948 (20/20 0:0): 8 too_many_variants (9p21_CDKN2A 18,792; BMI_5q13_3 30,702; PYHIN1_1q23 34,128;
  SLC2A9_urate 20,523; both arms), 12 fit (APOE_19q13 15,136 and CXADR_F2RL1_6p21 13,913 under the cap; planning expected up to
  12 early exits).
- Cost (`$Q/cost_15_7h2.tsv` 3edd5553…): sample Slurm 2026078 at 48G: routeC APOE_19q13 3:17, MaxRSS 9,546,352 KiB; k2d
  APOE_19q13 50:45, MaxRSS 42,565,388 KiB (84.6% of 48G; over the original 40 GB gate). Remaining 18: Slurm 2036650 (k2d, 56G,
  -t 02:00:00, an orchestrator resource change, not a Carter decision) max MaxRSS 33,720,796 KiB (CXADR_F2RL1_6p21, 57.4% of 56G,
  28:06); Slurm 2036651 (routeC, 48G, 1 h) ≤ 8.3 GiB. 20/20 outputs; split reproduced; policy_hash 60c195cb… on all 12 fits;
  nothing under data/r4/results.
- Pilot fits: manifests/proxy_asthma_pilot_fits_sha256.tsv (652195c7…), 40 files = 12 fits (24 files) + 8 early exits
  (16 files), pre-lock pilot fits, never a proxy or lock input. For 15.7i: 12 pilot fits (24 files).
- Proxy with asthma (Slurm 2037096; evidence only): `$Q/proxy_15_7h2.tsv` 2be5f5e3…986f, `$Q/proxy_15_7h2_fits.tsv`
  9c44721f…2775; 81 fits rows; routeC asthma CXADR_F2RL1_6p21 unmapped (41 of 4,516 members; the fit ran on catalog positions).
- Build check (Slurm 2039532): build_check.tsv 651163d3…a63e (committed as manifests/w3f_157h2_build_check.tsv), .py e595233b…,
  .sh 014ee178…; coordinate_frames.txt 652b5d7c…. variants_r4: 30 of 31 regions have joined rsids, all at the GRCh37 production
  asthma positions (BMI_Xq24 has 0 joined rsids; NC_IRF4 also matches the GRCh38 file, the builds coincide there).
  variants_legacy is in the GRCh38 frame (config/ta_r4/data_sources.yaml:66).
- Recorded proxy (Slurm 2039595, asthma excluded, exact purity): `$Q/proxy_15_7h2_noasthma.tsv` 78e0f85e…7927,
  `$Q/proxy_15_7h2_noasthma_fits.tsv` fb2ac330…a464. 69 rows, 0 asthma rows; keys and every column equal job 2037096's 69
  non-asthma rows (`$Q/noasthma_vs_2037096.txt`; NCs one-cell mutation and dropped row both detected). scored_matrix:
  repro_k2d_routeC identity 34; repro_routeC regularized 21, panel 14; unmapped 0. The 5 probe fits regularized, t2d.SH2B3_12q24
  panel. stored = exact on every fit (k2d 0 changes). Totals A1_matched likely 8 / unknown 1 / unlikely 1; A2_identity likely 3 /
  unknown 2 / unlikely 5; k unknown. FLAG lines verbatim in the DRAFT and HANDOFF.
- w3f_region_contribution_proxy.tsv: the re-run is byte-identical to the committed manifest (cmp), 0 rows changed. DRAFT
  Pre-Paste proxy row and HANDOFF region_contribution_proxy relabelled (old text under region_contribution_proxy_PRE_2026_11_20);
  test_amendment_text.py 21 P / 2 S. Commit dd5eb803.
- FULL Slurm 2039942 (cascadelake c022n01, HEAD dd5eb803, --mem=64G -t 06:00:00): QUICK 860 P / 2 S; HEAVY 330 P / 5 S; PINS 39 P;
  FULL 2,691 = 2,638 P / 53 S / 0 F (full_15_7h2.xml 50827ce7…). vs full_15_7h.xml: 0 removed, +9 (all passed), 0 outcome
  changes. `$Q/check_15_7h2.py` CHECK PASS rc 0; its NC (base as new) CHECK FAIL rc 1.
- No push, no production fit, no colocalization, decision_rules.yaml locked: false, no OSF, n_regions_min 7.

## 2026-11-24 — W3f 15.7i (F15 pre-lock pilot-fit disclosure: recount, manifest, v3 wording in DRAFT (h); Carter Q-F15 A, Q-F15W, Q-F15V3; no push)

- Start 61d6eebd (`$Q/start_15_7i.txt`). Gates (`$Q/gate_15_7i.txt`): gate_reply.py Q-F15 aaff9960…5877, Q-F15W 5bd31c68…ef05,
  v2 sha256 65c3851d…243b, rc 0; NCs wrong sha / wrong label / wrong v2 sha RED. DEC-2026-11-20-ta-r4-prelock-pilot-fit-disclosure
  quoting all three (cat + cmp rc 0; cross-file cmp RED), b343872f.
- Recount (`$Q/pilot_recount.txt`): pilot fits 146 → 166, reproduction-route fits 108 → 128 (15.7h2's 20 asthma outputs: 12
  fitted, 8 too_many_variants); 20 production-panel, 18 earlier-catalog, 17 kernel runs, 7 of 20 with ≥ 1 set (same list), 109
  purity components unchanged; 39 of the 128 stopped before fitting (31 + 8; too_many_variants 32, no_variants 7); 69 existing
  repro fits with exact purity in the recorded proxy (plan said 70 at planning); 0 asthma fits in it. recount_matches_v2=false.
- Coloc search Slurm 2041110 (`$Q/c157i/coloc_search_2041110.out`): 32 coloc-named files since 2026-11-09, 0 mention
  measure_asthma_fix (only hit the search script); planted plain + gzip NCs found; sacct: no coloc job since 2026-11-09.
  Slurm 2041108 cancelled (path match hit every file under coloc_analysis/).
- Manifest manifests/prelock_pilot_fits.tsv (bb7ca0ea…; 366 files = 183 fits × json+rds; builder `$Q/c157i/build_prelock_manifest.py`);
  15.7h2's 40 asthma files sha256-equal to proxy_asthma_pilot_fits_sha256.tsv. Tests 1-2 RED with the manifest absent
  (`$Q/red_15_7i.txt`), GREEN; NCs unlisted file / wrong sha / missing file RED, restore byte-identical (`$Q/green_nc_15_7i.txt`). 42f3eb9c.
- Task 2 STOP (human-action). v3 draft `$Q/F15_wording_v3_draft.txt` (760a1989…): template's proxy sentence false under
  Q-DROPASTHMA and double-counted the 20, redrafted. Carter: "v3 + all early exits (Recommended)" (draft + 39-of-128 sentence).
  Gate Q-F15V3 d195a0a4…e049 + v3 sha 67cb9a11…83a1 rc 0; NCs plan label / wrong sha / wrong v3 sha RED (`$Q/gate_15_7i_v3.txt`);
  word diff vs draft = exactly Carter's two changes; 39 = 31 + 8 confirmed. Reply + wording files, DEC addendum (cmp rc 0),
  plan <question> pins: ac61c486.
- DRAFT (`$Q/draft_15_7i.py`): purpose line "production-arm fit" (unique); v3 appended to (h), hard wraps removed (295 words),
  asserted equal. Test 3 GREEN; NCs pre-insert DRAFT / one number changed / v2 also present RED. test_amendment_text.py 21 P / 2 S
  (FINAL/PUBLIC absent, as in the base). 46e0b1fe.
- FULL Slurm 2080101 (c200n03, Haswell; submitted without --constraint=cascadelake): 5 pre-existing tests failed on the job
  guard's CPU check (test_in_job_gate drift test, 4 test_snakemake_toy_e2e); kept as `$Q/full_15_7i_haswell_2080101.xml` +
  `$Q/check_15_7i_haswell_2080101.txt` (CHECK FAIL). Resubmitted with the constraint used by every earlier close.
- FULL Slurm 2083696 (cascadelake c021n03, HEAD 46e0b1fe, --mem=64G -t 06:00:00): QUICK 861 P / 2 S; HEAVY 332 P / 5 S; PINS 39 P;
  FULL 2,694 = 2,641 P / 53 S / 0 F (full_15_7i.xml 1e2b9312…). vs full_15_7h2.xml: 0 removed, +3 (all passed), 0 outcome changes.
  `$Q/check_15_7i.py` CHECK PASS rc 0; NCs (base as new; the Haswell run) CHECK FAIL rc 1. Target 2,694 (plan said 2,692 on a
  stale 2,689 base; orchestrator-signed arithmetic correction). 15.7j's FULL base = full_15_7i.xml (2,694).
- No push, no production fit, no colocalization, decision_rules.yaml locked: false (unchanged), no OSF, n_regions_min 7.

## 2026-11-24 — W3f 15.7j (15.7 close): DRAFT (m)/Pre-Paste, text-vs-code check, brief-blind re-review

- Start HEAD 72e4d1f4 (`$Q/start_15_7j.txt`). DRAFT edit `$Q/draft_15_7j.py` (one script, each old string asserted
  unique; `$Q/draft_15_7j.txt`): (m) gains the 13 15.7 code/manifest commits with labels (420aa998, 5fce26a8, e1422df1,
  1cf179d1, 8d272492, 57ddb59d, c3c76ba2, 7405ba4a, 0e6dda24, 350cd9b9, 265434df, bcd0310a, 42f3eb9c); Pre-Paste
  analysis-code row gains them by plan; the F-list OPEN row → 12 rows (F1 F2 F3 F4 F6 F7 F8 F9 F10 F11 F12 F15). (m)
  carries 47 distinct shas = 34 (15.6) + 13; `git merge-base --is-ancestor` 47/47 (NC: a bogus sha → rc 128).
  test_amendment_text 21 P / 2 S.
- Text-vs-code, F1–F15 at HEAD 72e4d1f4 (code unchanged in 15.7j):

| F | code at HEAD | DRAFT clause | match |
|---|---|---|---|
| F1 | src/python/ta_r4/job_guard.py:95-119 (lock gate, config digest, Cascade Lake, OPENBLAS_* env, record); commands.py:108 (first command of every production job); bin/r4_fire.sh:65 (production refuses --config/--configfile/--profile/...) | (k) "each production job refuses to run on another CPU type, with `OPENBLAS_CORETYPE` set, or under a run configuration that differs from the committed configuration files, and records what it checked" | yes |
| F2 | run_susie_rss.R:713, :772-776, :1216 (`--exact-purity` → n_purity = nrow(subset)); run_qtl_coloc.R:82, :155; commands.py:49 (production arms pass it); simulate_coloc_r4.R:62 (n_purity = length(z)) | (k) "set purity is computed over all pairs of set members, for GWAS and QTL fits and in the simulation" | yes (production; repro arms and QTL_legacy keep susieR's default, and are not estimand inputs except QTL_legacy as the E7 comparator) |
| F3 | assign_tiers.py:85-118 (sweep with gwas_best → tier definitions; no table → legacy, logged); :310, :359 (`--nan-gwas-below-threshold`); run_qtl_group_r4.py:277-280 (tiers_argv passes it); ta_r4_qtl.smk:152-174 (r4_qtl_tiers for every R4 QTL arm, QTL_legacy included via repro_routeL, run_qtl_group_r4.py:33) | (l) "the PP.H4 threshold sweep applies the tier definitions … and a region whose trait-pair rows have no PP.H4 (all method `none`) is below threshold" | yes for all three R4 QTL arms. NOTE: the Q-F3N question text says QTL_legacy "does not get the flag"; the code gives it the flag (OPEN item for Carter, W3f157_QF3N_premise) |
| F4 | run_aggregation.py:181-214 (replicate ids 1..reps per arm via id_reconcile.reconcile, row labels, seeds, header config_sha256) | (g) "each with exactly the configured 200 replicates per arm" | yes |
| F6 | run_aggregation.py:312-328 (QTL summary ids == qtl_manifest qtl_row_id once each; no empty method) | (e) "final tables are written only when colocalization coverage is exact (no missing or extra outputs in any arm)" | yes |
| F7 | run_qtl_group_r4.py:138-146 (`_empty_reason`: coloc_susie_empty / coloc_susie_no_finite_h4 → none) | (l) "So are rows for which `coloc.susie` returns no summary or no finite PP.H4." | yes |
| F8 | estimands.py:607-614 (negative_control_rates by (nc_set, label, p12_key) and method, + with_posterior) | (l) "share of rows with S ≥ 0.8 per set, arm and method (…); rows with method `none` are counted and are in no denominator" | yes |
| F9 | select_null_windows.py:96-114 (manifest_sha256 on the production inputs); manifests/null_windows_selection.tsv (2,886 candidates) + .superseded-2026-10-21.tsv | (l) "10 of the 2,886 candidates on the corrected inputs … an earlier draw from a 2,865-candidate pool … is superseded; 2 of its 10 windows are in the current selection" | yes |
| F10 | cs_cross_purity.R:4-5, :20, :57-58 (resolve_fit_names, variant_match.R) | (e) E4 "a member being identified through the fit's own summary statistics and panel and located by position and alleles" | yes |
| F11 | estimands.py:317-326 (`_no_cs` known zero; `_unknown_cs`); run_coloc_pair_r4.R:517 (completed side keeps n_cs) | (e) E4 "a trait whose fit exited early has no count, and a row with no known zero and such a side is counted as unknown; rates over the arm's pair rows and over its rows of known state" | yes |
| F12 | run_aggregation.py:61-62, :400, :418 (a1_allvars_secondary EUR/AFR; drop family) | (e) E6 "A1 on all variants (`allvars`) is reported the same way against `A3_1kg` (EUR) and `AFR661_A3` (AFR)" | yes |
| F15 | manifests/prelock_pilot_fits.tsv; tests/ta_r4/test_prelock_pilot_fits.py (disk + sha256 + paragraph == approved v3 file) | (h) **Pre-lock pilot fits.**; Purpose "before any production-arm fit exists" | yes |

  No mismatch requiring a DRAFT change before the review (step 2).
- Review (brief-blind, as 15.6): prompt `$Q/codex_prompt.md` = 15.6's wrapper bytes (prefix/suffix byte-equal) + the
  extract (4,909 words, sha256 ab115483…89dc); prompt sha256 a16f75f7…2bc5; codex-cli 0.166.0 (W4a scratch install),
  `-m gpt-6.1-sol`, read-only, rc 0 first attempt, 21:32:30 → 21:56:02 EST; output 37,290 B sha256 6d2060d7…1fe0,
  banked in `ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md` (embedded block cmp-equal to raw stdout; NC: one changed
  word → cmp rc 1). 14 findings (R1–R7 + Q1–Q7) = 14 rows: DRAFT fixed 7 (R2 R3 R5 R7 Q1 Q4 Q5; 6 replacements,
  `$Q/draft_fix_15_7j.py`), OPEN for Carter (code) 2 (R4 QTL JSON 4-decimal rounding before thresholds; R6 BLAS
  library unpinned and the committed env lock is not the job env: job env libopenblas 0.3.34, named-env lock 0.3.32),
  code follow-ups on R2 (collector drops unaudited) and R3 (optional), rejected 1 (R1), noted 4. Plus the executor's
  Q-F3N premise item (QTL_legacy does get the NaN flag). test_amendment_text + test_prelock_pilot_fits 24 P / 2 S; NC
  "pivot" → test_draft_extract_framing FAILED, restored sha256-equal. Extract 4,909 → 5,012 words.
- Own slip, fixed before commit: step 1's Pre-Paste F15 row quoted `**Pre-lock pilot fits.**`, which made
  test_prelock_pilot_fits' count assertion 2 ≠ 1 (step 1 had run only test_amendment_text). Row text changed to
  "pre-lock pilot-fit paragraph" in the DRAFT and in draft_15_7j.py.

## 2026-11-25 — W3f 15.7j close: FULL reconciled cumulatively; records completion; HANDOFF / STATE / PLAN-INDEX (no push)

- FULL Slurm 2086699 (`--constraint=cascadelake`, c020n02, HEAD 99ab219d, 64G, 2h13m): QUICK 861 P / 2 S (5m50s; over the
  120 s guide, as 15.7a–i); HEAVY 332 P / 5 S; PINS 39 P; FULL 2,694 = 2,641 P / 53 S / 0 F (`$Q/full_15_7j.xml` 27b0596e…).
  src/, tests/, config/ta_r4 clean.
- `$Q/check_15_7j.py` (ids and declared spec updates parsed from the ten 15.7 SUMMARYs) first STOPPED, rc 3: 15.7h had no
  id list; 15.7h2 had no id list and no `## Declared spec updates` section (127 of 140 ids). Handed back; orchestrator
  sign-off 2026-11-25: both SUMMARYs gained `## New test ids` copied from `$Q/new_tests_15_7h.txt` (4) and
  `$Q/new_tests_15_7h2.txt` (9), and 15.7h2 `## Declared spec updates` none, labelled "records completion, 15.7j". Parser
  header match widened from "New tests" to "New test".
- Strict re-run on the same xml (`$Q/reconcile_15_7j_strict.txt`): CHECK PASS rc 0. Per plan 32 + 31 + 18 + 7 + 12 + 13 + 11
  + 4 + 9 + 3 = 140 (15.7d's 7 = 6 new + the rename successor); vs full_W3f.xml removed 1 = the declared _19_ → _20_ rename
  (successor passed), added 140 = the SUMMARY union, all passed, 0 outcome changes (27 declared spec-update ids, all passed),
  2,555 + 140 − 1 = 2,694, skips 53; vs full_15_7i.xml identical by id and outcome (junit_cmp 0/0/0, tests/m3 0). NCs
  (`$Q/check_15_7j_strict_nc.txt`): base as new FAIL rc 1; Haswell 2080101 FAIL rc 1; a SUMMARY copy without 15.7h2's spec
  section STOP rc 3.
- Q-F3N (W3f-carter-15-7-Q-F3N-reply-2026-11-24.txt, sha256 eaafba6e…d3e3, gate rc 0, wrong-label NC rc 2) committed;
  DEC-2026-11-20-ta-r4-qtl-sweep-gwas-pph4 addendum quotes it (quoted block cmp-equal to the file; DECISIONS.md insert-only)
  and records the wrong premise and Carter's corrected answer Q-F3NL 2026-11-25 (→ 15.8).
- HANDOFF (`$Q/handoff_15_7j.py` → target dict; applied as line edits by `$Q/handoff_15_7j_textual.py` because the file mixes
  escaped and literal non-ASCII; result == target): 12 W3f_F* → RESOLVED (old under _PRE_2026_11_20); W3f157_R2–R7 +
  W3f157_QF3N_premise as decided by Carter → 15.8; read_first + the 15.7j review; region_contribution_proxy per 15.7h2 (old
  under _PRE_2026_11_25, FLAG lines kept); headline / status / suite_baselines_ta_r4_latest / resume_on_reconnect rewritten
  (old under _PRIOR_2026_11_25); ta_r4_w3f_15_7j_close. Keys 401 → 429; 488 pre-existing strings all present (NC: one PRE
  key deleted → 1 missing). confirmatory_sha256 9fa410aa…88d5 re-measured, unchanged.
- W4a PLAN untouched (depends_on stays; 15.8f sets it). PLAN-INDEX 15.7j COMPLETE; STATE ★ block NEXT = 15.8.
- No push, no fit, no OSF, decision_rules.yaml locked: false, n_regions_min 7, no signoff file.

## 2026-11-25 — W3f 15.8a (R2 collector drop audit; Carter Q-157J, Q-158R2 D; closed on its B path; no push)

- Commits (local only): 159c06ad (15.8 planning set, PLAN-INDEX 15.8 rows + protocol, the six reply files as received,
  DEC-2026-11-24-ta-r4-w3f-15-8-open-items), 06b68482 (collector_drop_audit.py, tests 1-6, catalog_collector_drops.tsv),
  8da7bfbe (Q-158R2 reply, DEC addendum, reply sha256 pinned in the plan), plus the records commit.
- Gates (`$Q8=data/r4/tmp/w3f/q158`): gate_157j.sh (free text with "pin  libopenblas", two spaces), gate_158.sh (5 QIDs),
  gate_158r2.sh (4183859f…bacb, label D), all rc 0. NCs rc 2: a one-byte-changed staging copy (cmp, and the tool alone
  via sha256); one space instead of two; an unknown QID; for Q-158R2, a wrong question and label A
  (gate_nc_15_8a.txt, gate_158r2_15_8a.txt). full_15_7j.xml is identical by id to full_15_7i.xml (2,694 = 2,641 P / 53 S).
- Premise: collect_region_variants.py drops at rsid keying (:104-123), unnamed repeats (:106-109), :142 (no-op, 0
  rows), :143-150 and :151-155. The replay holds identity with the unmodified collector, and its TSV is byte-equal to
  variants_r4_raw, in 31/31 regions (Slurm 2092056). 1,598,153 input = 875,225 kept + 722,928 dropped; 0 rows of class
  `other`. Classes: exact_duplicate 358,583; rsid_same_key_other_bytes 57,009; rsid_other_allele_key 216,218;
  unnamed_duplicate 33,842; unnamed_at_named_position 57,119; unnamed_same_position_other_alleles 157;
  rsid_replaced_allele_less 0; allele_less 0. Per region: manifests/catalog_collector_drops.tsv.
- Lost keys: 162,724 rows / 67,626 distinct keys (159,969 / 65,753 with the swapped key in the catalog); 39,103 distinct
  keys are in at least one production panel (Slurm 2092136-2092139). STOP at Task 2 → Q-158R2. The orchestrator measured
  (Slurm 2092423) that the fit's exact catalog join drops the reversed-orientation rows: hypertension EUR 33.5%, stroke
  EUR 33.6%, stroke AFR 29.4%, t2d AFR 21.9%, asthma AFR 1.5%, asthma EUR 0.6%, bmi/t2d EUR 0%. Recomputed here from
  `$Q8/orient_by_fit.tsv` (b154b0fa…c4f1): equal. Carter: "D: Harmonize r4 sumstats to one orientation
  (Recommended)" → plan 15.8a2.
- **R2: audit done; the lost-key consequence is the orientation drop; fix = Carter D, plan 15.8a2.** B path: no test 7,
  no DRAFT (c) edit; review row R2 stays OPEN.
- Test 6 timed at 603 s in Slurm 2092140 (NC_ABO, the fewest input rows) and 493 s inside FULL; under 15 min, not reduced.
- NCs (`$Q8/nc_15_8a.txt`): (a)-(d) module mutations RED as planned; identity guards (e3) and (f) refused; (e) refused
  by the accounting guard instead, and (e2) not discriminating on NC_ABO (82/82 rows at CHR:POS-named positions,
  checked); test 6 manifest tampering ×3 RED; catalog sha cmp RED; panel-measurement controls as expected.
- FULL Slurm 2093289 (cascadelake c020n02, HEAD 8da7bfbe, 2h29m): QUICK 866 P / 2 S; HEAVY 333 P / 5 S; PINS 39 P; FULL
  2,700 = 2,647 P / 53 S / 0 F (full_15_8a.xml 41fdc36e…4d8c). check_15_8a.py against full_15_7j.xml: 0 removed, +6,
  0 changes, CHECK PASS; NC (base as new) FAIL rc 1.
- Catalog sha256 before == after (95 lines). No push, no fit, no OSF, decision_rules.yaml locked: false, n_regions_min 7.

## 2026-11-25 — W3f 15.8a2 (r4 sumstats in the r4 catalog's orientation; Carter Q-158R2 D, Q-158OR A, Q-158PAL A; no consumer switched; no push)

- Commits (local; see note on bda956a0 below): 1298b511 (15.8a2-a4 PLANs, 15.8b-f amendments, the Q-158OR / Q-158PAL /
  Q-158EL replies as received, DEC-2026-11-25-ta-r4-sumstats-orientation, PLAN-INDEX 15.8a2-a4 rows + order line + base
  chain), 859458f9 (sumstats_orient.py, 14 tests, three manifests), plus the records commit. bda956a0 (a HANDOFF/STATE
  commit made from the orchestrating session during this plan) is not an executor commit.
- Gates (`$Q8=data/r4/tmp/w3f/q158`): gate_157j.sh, gate_158r2.sh, gate_158a2.sh Q-158OR Q-158PAL (new; `--question` =
  the plan's text minus its leading `<QID> `, generated from the plan's <question> block), all rc 0. NCs rc 2
  (a2/gate_nc_15_8a2.txt): one byte changed in a staging copy (Q-158OR, Q-158PAL); one character of the Q-158OR text
  changed; the question typed with its leading QID; only a non-Recommended label allowed; one sha256 character changed;
  an unknown QID. Reply sha256: Q-158OR b4a87020…646a, Q-158PAL b5cde5c3…ec13, Q-158EL f4ecd066…409c (committed, gated
  in 15.8a4), Q-158R2 4183859f…bacb. DEC quotes cmp-equal to the files (NC: one character changed → DIFFER).
- Sources: CATALOG_SOURCES == paths.sumstats_path(t, a, "A3_1kg") == collector_drop_audit.r4_sumstats() at 1298b511
  (a2/sources_check.txt). Before-state: 44 files sha256 (a2/sha_before.txt); verify_inputs on the 8 inputs OK.
- Per file (harmonize reports a2/report_<t>.<a>.json; bgzip/tabix htslib 1.9):

| file | lines | window rows | exact | swapped_only = flipped | both | absent | flipped A/T-C/G | of them EAF 0.4-0.6 | oriented sha256 |
|---|---|---|---|---|---|---|---|---|---|
| bmi.EUR | 2,327,244 | 24,881 | 12,906 | 0 | 11,975 | 0 | 0 | 0 | ed3a7276… |
| t2d.EUR | 25,677,382 | 376,940 | 364,527 | 0 | 12,413 | 0 | 0 | 0 | 039d1c01… |
| t2d.AFR | 19,257,160 | 253,745 | 153,327 | 55,567 | 44,633 | 218 | 9,748 | 612 | 33568f85… |
| hypertension.EUR | 7,160,657 | 104,047 | 56,921 | 34,871 | 12,131 | 124 | 5,951 | 611 | 49a337bc… |
| asthma.EUR | 27,843,603 | 377,364 | 345,303 | 2,412 | 28,378 | 1,271 | 784 | 17 | 2634c5b4… |
| asthma.AFR | 20,231,905 | 261,183 | 213,118 | 3,798 | 43,446 | 821 | 1,347 | 13 | ef8896f6… |
| stroke.EUR | 7,511,476 | 107,772 | 59,222 | 36,195 | 12,257 | 98 | 6,227 | 624 | 4b8d42ce… |
| stroke.AFR | 5,259,724 | 92,221 | 52,293 | 27,126 | 12,579 | 223 | 4,580 | 510 | 27b6e32e… |
| total | | 1,598,153 | 1,257,617 | 159,969 | 177,812 | 2,755 | 28,637 | 2,387 | |

- Identities (a2/identities.txt, Slurm 2094864; idempotence Slurm 2094863): (a) measure on the 8 catalog-source files ==
  orient_by_fit.tsv (b154b0fa…c4f1) row for row, 248 rows; (a2) the streaming harmonize counts == the tabix measure per
  region × trait; (a3) verify_unflip passed on all 8 files (n_flipped, n_lines equal); (a4) duplicate allele keys 12
  before = 12 after (asthma EUR/AFR × HLA_6p21 only); SNP_IDs with more than one catalog-joined key 0 before, 0 after;
  (b) on the 8 oriented files swapped_only == 0 in 248/248 rows, after_exact == exact + swapped_only, after_both == both,
  absent and n_rows unchanged; (c) harmonize() on each oriented file flips 0 rows and its output cmp-equals the
  decompressed oriented bytes, 8/8 (NC: one byte changed → cmp rc 1); (d) per source file n_flipped == 15.8a audit rows
  with key false / swapped true and absent == audit rows with both false: t2d AFR 55,567 / 218, hypertension 34,871 /
  124, asthma EUR 2,412 / 1,271, asthma AFR 3,798 / 821, stroke EUR 36,195 / 98, stroke AFR 27,126 / 223, bmi and t2d
  EUR 0 / 0; totals 159,969 and 2,755; (e) the 8 inputs, every data/processed file in sumstats_r4_sha256.tsv, the 31
  catalogs and the manifest: sha256 before == after (44 files) before pinning.
- Pinned: 16 rows (8 oriented files + .tbi, role output) appended to sumstats_r4_sha256.tsv; `diff` against
  a2/sumstats_manifest_before.tsv shows only the appended lines; each equals its harmonize report sha256; verify_inputs on
  16 + 8 OK.
- EAF diagnostic (manifests/sumstats_r4_orientation_eaf.tsv, not a filter; median |ΔEAF| flipped / unflipped):
  hypertension 0.0167 / 0.0164, stroke EUR 0.0157 / 0.0155, stroke AFR 0.0057 / 0.0058, t2d AFR 0.0026 / 0.0021, asthma
  AFR (vs t2d AFR) 0.0019 / 0.0022 with 0 of 2,355 flipped above 0.2, asthma EUR 0.0270 / 0.0047 with 19 of 225 flipped
  above 0.2. The planner's numbers reproduce except asthma EUR flipped (planner 0.0225, 5 of 204): its asthma_eaf.py kept
  single-base SNVs only, while this table follows the plan's rule (every non-palindromic row, indels included: 225).
  Checked: the SNV subset of this run gives 204, 0.0225, 5 above 0.2 (planner exactly); the 21 flipped asthma EUR
  indels carry 14 of the 19 above 0.2. Recorded for 15.8a4 / Carter, not a filter (unflipped rows are not filtered by
  EAF either).
- NCs (`$Q8/nc_15_8a2.txt`): (a) flip on swapped_only or both → test 3 RED; (b) str(-float) BETA → test 2 RED on
  `0.0100`; (c) str(1 - float) EAF → test 2 RED on `0.8365` (`0.16349999999999998`); (d) duplicate check removed → test 5
  RED; (e) verify_unflip skips outside-window lines → test 8 RED; (f) test 9 _compare on a copy with one count byte
  changed → RED; (g) test 10 _check_oriented on the source files → RED; (h) test 11 with one audit count +1 → RED; (i)
  test 12 with one sha256 character changed in an appended row and in a pre-existing data/processed row → RED both; (j)
  test 14 on a re-bgzipped oriented stroke.AFR with one SE changed on an unflipped in-window line → RED.
- Timings: harmonize 1:01-3:22 per file (max RSS 633 MB), verify_unflip 0:14-2:13; tests 9 / 10 / 12 / 14 19 s / 19 s /
  22 s / 27 s (Slurm 2094929); none near 15 min, none reduced.
- FULL Slurm 2094979 (cascadelake c020n02, HEAD 859458f9, 2h27m): QUICK 875 P / 2 S; HEAVY 338 P / 5 S; PINS 39 P;
  FULL 2,714 = 2,661 P / 53 S / 0 F (full_15_8a2.xml 63e6db93…15ef). check_15_8a2.py against full_15_8a.xml: 0 removed,
  +14 (the 14 new ids, all passed), 0 outcome changes, CHECK PASS; NC (base as new) CHECK FAIL rc 1.
  tests/m3/sparse_parent_benchmark.tsv restored by close.sh (clean). After the pin, the 44-file sha256 differs from
  before only in sumstats_r4_sha256.tsv (a2/sha_after.txt).
- No consumer reads the oriented files (paths.sumstats_path unchanged; 15.8a3 switches). No catalog, panel or
  data/processed byte changed. No fit, no OSF, decision_rules.yaml locked: false, n_regions_min 7. NEXT = 15.8a3.

## 2026-11-25 — W3f 15.8a3 (r4 production reads the oriented sumstats; catalogs, collector audit and pilots keep their inputs; catalog fixed point 31/31; no push)

- Commits (local): 9b5876c9 (paths split + consumer switch, data_sources r4_oriented records, fixture copy, tests 1-6,
  5 declared spec updates), 50a7bad9 (manifests/catalogs_r4_fixed_point.tsv, tests 7-8), plus the records commit.
- Gates (`$Q8=data/r4/tmp/w3f/q158`, a3/gates.txt): gate_157j.sh, gate_158r2.sh, gate_158a2.sh Q-158OR Q-158PAL, all
  rc 0 (sha256 805afcd8…503e, 4183859f…bacb, b4a87020…646a, b5cde5c3…ec13). 15.8a2 closed (SUMMARY 83e17b38,
  full_15_8a2.xml present). Start HEAD 83e17b38 (a3/start.txt).
- Before-state: sha256 of the 31 raw / final / dropped r4 catalogs, catalogs_sha256.tsv, catalogs_r4_unique_key.tsv and
  the 11 panels_*.tsv (106 files, a3/sha_before.txt); paths.sumstats_path for every arm × the 8 pairs (a3/paths_before.tsv).
- Consumers as executed:

| consumer | arm(s) | reads now |
|---|---|---|
| commands.fit_command / verify_command / coloc_command (susie, A1_matched, A1_allvars) / coloc_verify_command | 8 production arms | data/r4/sumstats/<t>.<a>.r4_oriented.tsv.bgz (test 1) |
| run_qtl_group_r4.abf_command / group_inputs | QTL_A3, QTL_A2 | oriented (test 1) |
| run_aggregation._cross_purity fit_sumstats | the 8 CROSS_PURITY fit arms | oriented (test 1) |
| measure_fit_eligibility.pinned_inputs / measurement_argv | production | oriented (declared updates 1-2) |
| coloc_command, run_qtl_group_r4 | repro arms, QTL_legacy | data/processed/sumstats_harmonized (unchanged, test 2) |
| ta_r4_panels.smk CATALOG_SUMSTATS["r4"] (r4_catalog_raw) | catalog build | catalog sources (test 4 dry run, collector order) |
| collector_drop_audit.r4_sumstats | 15.8a audit | catalog sources (test 5) |
| measure_fit_eligibility.ASTHMA_PILOT_SUMSTATS | pilot fits, region-contribution proxy | the corrected lift (test 5, declared update 3) |
| sumstats_orient.CATALOG_SOURCES / oriented_path | 15.8a2 harmonizer | unchanged typed sources; oriented_path → paths.oriented_sumstats_path (test 3) |

- Path diff (a3/paths_diff.txt, paths_before → paths_after): each of the 8 production arms × 8 pairs → `.r4_oriented.`
  (64 changes); each of the 5 repro arms × 8 pairs unchanged (40). catalog_source_sumstats_path over the 8 pairs ==
  the A3_1kg column at 83e17b38 in collector order == sumstats_orient.CATALOG_SOURCES == set(PRODUCTION_INPUTS).
- data_sources.yaml: each of the 8 sumstats entries gains `r4_oriented: {path, sha256, from}`; no other key changed
  (asserted on load). `from` = the file the copy was made from (the 15.8a2 report's src): the entry's url for 7 entries;
  for bmi EUR it is data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz (D-18), not its url (data/processed bmi.EUR) — see
  SUMMARY deviation 1.
- RED (`$Q8/red_15_8a3.txt`, Slurm 2096701, old code): tests 1, 3, 6 and declared updates 1-3 FAILED; tests 2, 4, 5
  PASSED (characterization). Need of declared updates 4-5 after the switch (Slurm 2096713, both unedited):
  test_qtl_abf_maps_bridged_names_through_panel FAILED (`n_direct` 196 != 0: QTL_A3 read the un-rewritten r4-route copy);
  test_real_asthma_eur_sumstats_verifies' unedited `rel` = data/r4/sumstats/asthma.EUR.r4_oriented.tsv.bgz (it would
  have silently changed subject and still passed). Then edited; both pass.
- Suite after the switch (Slurm 2096746, cascadelake): QUICK tests/ta_r4 880 P / 2 S (15.8a2 875 + 5 new); r4_heavy in
  the 14 listed files + the new file 86 P / 0 F; per id vs full_15_8a2.xml: 0 outcome changes; the 5 qtl_group_fixture
  importers (test_qtl_group_runner, test_coloc_pair_r4, test_verify_inputs, test_fit_name_alignment,
  test_purity_determinism) collect and pass.
- NCs (`$Q8/nc_15_8a3.txt`, Slurm 2096854; md5-restored, PYTHONDONTWRITEBYTECODE=1): (a) sumstats_path returns the
  source for A3_ukb → test 1 RED; (b) CATALOG_SUMSTATS["r4"] from sumstats_path → test 4 RED; (c) ASTHMA_PILOT_SUMSTATS
  from sumstats_path → test 5 and the declared proxy test RED; (d) oriented path for repro_routeC → test 2 RED; (e)
  r4_sumstats from sumstats_path → test 5 RED. After restore the 5 tests pass.
- Catalog fixed point (a3/fixed_point.py, Slurm array 2096913_[0-30], 6-7 min per region, max RSS 3.2 GB): per region
  the 8 oriented files (collector order, all present, verify_inputs OK) → collect_variants → `to_csv(sep="\t",
  index=False)` → catalog_unique_key.unique_allele_key rendered as its main() writes it; raw, final and dropped bytes
  equal the pinned files in **31/31** regions (fp_outcome=0; no Q-158FP). Totals: raw 875,225 (= 15.8a n_kept), final
  627,685, dropped 247,540.

| region | raw rows | final rows | dropped rows | raw / final / dropped sha256 (pinned = rebuilt) | equal |
|---|---|---|---|---|---|
| 9p21_CDKN2A | 54,234 | 40,526 | 13,708 | 462a355e… / 5e17c5e5… / f341e1e0… | true |
| APOE_19q13 | 48,629 | 35,222 | 13,407 | 86a9e906… / eb3cfb66… / e1330262… | true |
| APOL1_22q12 | 8,380 | 5,983 | 2,397 | 95c29ec5… / d4d5d6b3… / b7338ad1… | true |
| BMI_5q13_3 | 92,558 | 67,249 | 25,309 | a7f791ca… / 4e646dfb… / 0f8fb21a… | true |
| BMI_Xq24 | 23,214 | 23,214 | 0 | 1e9b2dd0… / 1e9b2dd0… / 0b65697d… | true |
| CXADR_F2RL1_6p21 | 37,945 | 27,308 | 10,637 | 242e745c… / 2bd29d9e… / 4256cd44… | true |
| FTO_16q12 | 14,410 | 10,334 | 4,076 | 09cab294… / 2927a05d… / 80e9b32e… | true |
| HLA_6p21 | 302,753 | 204,289 | 98,464 | 07f635eb… / 4cacd1e0… / 1751aef3… | true |
| MC4R_18q21 | 14,940 | 10,871 | 4,069 | 9a1d37df… / 369fa118… / 75265254… | true |
| NC_ABO | 1,068 | 773 | 295 | 6b05bc23… / 3c7c18fb… / ec917f59… | true |
| NC_FUT1_FUT2 | 1,362 | 990 | 372 | 253d13b1… / bb125bd6… / 2d5fea2b… | true |
| NC_IRF4 | 3,276 | 2,372 | 904 | dad5f8a2… / 48fc2b6d… / bea957da… | true |
| NC_KEL | 1,807 | 1,305 | 502 | 2ff7dc34… / 9df5ec7f… / 7a9a596b… | true |
| NC_MC1R | 5,774 | 4,112 | 1,662 | 0c02a823… / 1da42c45… / 263175b2… | true |
| NC_NULL_01 | 6,339 | 4,664 | 1,675 | f3d63ea7… / 5560b375… / bba1b0d6… | true |
| NC_NULL_02 | 6,122 | 4,432 | 1,690 | f2d66d13… / 9be97e67… / e014d962… | true |
| NC_NULL_03 | 5,249 | 3,827 | 1,422 | e0bea5df… / 2fc3da8f… / b1373d1d… | true |
| NC_NULL_04 | 6,094 | 4,512 | 1,582 | 30f1f1dc… / 98279afc… / 7e40f6b0… | true |
| NC_NULL_05 | 6,553 | 4,730 | 1,823 | 6e486059… / d3c2efad… / c38ac57d… | true |
| NC_NULL_06 | 6,096 | 4,553 | 1,543 | d6e8c31f… / c0600175… / b1226f84… | true |
| NC_NULL_07 | 7,878 | 5,614 | 2,264 | 4d80d100… / 2c4f595b… / cfbe6da7… | true |
| NC_NULL_08 | 6,292 | 4,580 | 1,712 | cbd6a6df… / 7d161599… / df04bd65… | true |
| NC_NULL_09 | 6,566 | 4,846 | 1,720 | 92e345dd… / 2a62ea7c… / 8ed93c8e… | true |
| NC_NULL_10 | 6,150 | 4,456 | 1,694 | 6e9402ef… / d15b07a8… / c58fcd36… | true |
| NC_OCA2_HERC2 | 10,307 | 7,393 | 2,914 | 974873ac… / a03eea07… / fc1f158e… | true |
| NC_RH | 2,640 | 1,963 | 677 | 2eef61b3… / 2afd9889… / 8887ada3… | true |
| NC_SLC24A5 | 9,989 | 7,534 | 2,455 | c1c94a97… / 87cbf5fa… / d48c2f7f… | true |
| NC_TYR | 12,955 | 9,610 | 3,345 | d342f0a8… / a1d0a22a… / 60374fb4… | true |
| PYHIN1_1q23 | 92,836 | 66,883 | 25,953 | e628afec… / 2dc5023d… / 2a4d382d… | true |
| SH2B3_12q24 | 11,114 | 8,140 | 2,974 | ef43ebe3… / 08afb93a… / 3f1d9d0e… | true |
| SLC2A9_urate | 61,695 | 45,400 | 16,295 | 1dca3c9d… / 54091524… / 78c47fd3… | true |
| total (31) | 875,225 | 627,685 | 247,540 | | 31/31 |

- Fixed-point NC (Slurm 2097246; the first run 2096917 stopped in the NC script before any comparison: `tabix -h` prints
  no header for a `-S 1` index; fixed): NC_ABO's first final-catalog row from bmi.EUR that is not A/T or C/G is
  9:136127268 C/T rs9411475; in a window copy of bmi.EUR.r4_oriented with sumstats_orient.flip_fields applied to that row
  only, fixed_point.py reports raw / final / dropped all **not equal** (raw: 1 row re-oriented, 0 added, 0 removed; final
  773 → 772, dropped 295 → 296: the flipped key collides with the other entry at that position), and test 7 on the same
  copy FAILS (byte diff `T` vs `C`). Test 8 with one manifest sha256 character changed FAILS (Slurm 2097324).
- After (Slurm 2097324): sha256 of the 106 files == before (`cmp a3/sha_before.txt a3/sha_after.txt`); tests 7-8 + the
  file + test_sumstats_orient.py 22 passed (test 7 208 s, test 8 1.5 s).
- FULL: Slurm 2097342 (cascadelake c022n03, HEAD 50a7bad9, 2h27m): QUICK 881 P / 2 S; HEAVY 340 P / 5 S; PINS 39 P;
  FULL 2,722 = 2,669 P / 53 S / 0 F (full_15_8a3.xml 0d538bd6…d988). check_15_8a3.py against full_15_8a2.xml (2,714 =
  2,661 P / 53 S, read from the file): 0 removed, +8 (the 8 new ids, all passed), 0 outcome changes, the 5 declared
  ids passed → passed, totals 2,722 / 2,669 / 53 / 0, CHECK PASS (check_15_8a3.txt); NC (base as new) CHECK FAIL rc 1
  (check_15_8a3_nc.txt). tests/m3/sparse_parent_benchmark.tsv restored by close.sh (clean). The 106-file sha256 is
  still equal to before after the FULL (a3/sha_after_full.txt).
- No production fit, no OSF, no lock; decision_rules.yaml locked: false, n_regions_min 7; no catalog, panel, sumstats or
  data/processed byte changed; Track B unchanged. NOT PUSHED. NEXT = 15.8a4.

## 2026-11-25 — W3f 15.8a4 (N1 eligibility re-measured on the oriented inputs; identities; re-pinned under Carter Q-158EL A; DRAFT orientation step, collector audit and eligibility; R2 resolved; no push)

- Commits (local): 5fb24630 (Q-158EL DEC bullet; the reply itself was committed as received in 1298b511), cda233a8
  (w3f_fit_eligibility.tsv re-pinned; tests 1-2), 8d8b7bb6 (DRAFT; tests 3-6), plus the records commit.
- Gates (`$Q8=data/r4/tmp/w3f/q158`, a4/gates.txt): gate_158a2.sh extended with Q-158EL (question = plan line 60 minus
  its leading `Q-158EL `, equal to reply line 1 after its prefix; sha256 f4ecd066…409c; label `A: Apply the cap as
  pre-registered and update the counts (Recommended)`). gate_158a2.sh Q-158OR Q-158PAL Q-158EL, gate_157j.sh,
  gate_158r2.sh: all rc 0. NCs (a4/gate_nc_15_8a4.txt): one byte changed in the copy, another label, one sha256
  character, the question typed with its QID: each exit 2. 15.8a3 closed (SUMMARY 14a9d265). Start HEAD 14a9d265.
- Measurement (no fit, SUSIE_MAX_VARIANTS=0): `measure_fit_eligibility plan --out-dir data/r4/tmp/elig_15_8a4
  --rscript …/r_coloc/bin/Rscript`: 83 tasks, keys == the 83 measured keys of the pinned table, every --sumstats an
  `.r4_oriented.` copy. Slurm array 2099709 (cascadelake), 83/83 COMPLETED 0:0 (a4/elig_sacct.txt). summarise: 815 rows,
  83 measured, not eligible 13.
- Identities (a4/identities.txt, a4/identities.py): (a) 0 of 732 bound rows differ outside sumstats_sha256; (b) bmi /
  t2d EUR 26 of 26 measured rows unchanged in n_variants_pre_ld and n_variants; (c) n_variants_pre_ld == after_exact +
  after_both of sumstats_r4_orientation.tsv in 83/83; (d) no n_variants fell; (e) Δn ≤ Δpre-LD in 83/83; measured
  catalog / panel sha256 and panel_n_var unchanged 83/83. PASS.
- Eligibility change set == the Q-158EL estimate set (label A → re-pin; Q-158EL2 not asked):

| fit | pre-LD pinned → oriented | after restriction pinned → oriented | eligible |
|---|---|---|---|
| AFR661_A3 t2d AFR × BMI_5q13_3 | 23,718 → 28,840 | 14,398 → 16,966 | true → false |
| AFR661_A2 t2d AFR × BMI_5q13_3 | 23,718 → 28,840 | 14,398 → 16,966 | true → false |
| AFR504_A3 t2d AFR × BMI_5q13_3 | 23,718 → 28,840 | 14,343 → 16,841 | true → false |
| AFR661_A3 / A2 t2d AFR × PYHIN1_1q23 | 22,260 → 27,281 | 13,341 → 15,832 | true |
| AFR504_A3 t2d AFR × PYHIN1_1q23 | 22,260 → 27,281 | 13,265 → 15,718 | true |
| A3_ukb asthma EUR × SLC2A9_urate | 26,934 → 27,241 | 14,263 → 14,402 | true |
| A3_ukb hypertension EUR × PYHIN1_1q23 | 7,495 → 10,786 | 6,414 → 9,154 | true |

  Every number equals the planner estimate (postld2.tsv). The 10 already-ineligible fits stay ineligible (asthma rises,
  t2d EUR unchanged). Not eligible per arm: A3_ukb 4 of 145; AFR661_A3, AFR661_A2, AFR504_A3 3 of 30 each; others 0;
  total 13 (was 10). Re-pin: a4/w3f_fit_eligibility.new.tsv → manifests/w3f_fit_eligibility.tsv (sha256 4a07d89c…3208
  → 1058dd64…554f; a4/sha_before.txt, sha_after.txt).
- NCs (`$Q8/nc_15_8a4.txt`, md5-restored): one measured n_variants_pre_ld +1 → test 1 RED; one row's sumstats_sha256 =
  the source pin → test 2 RED; framing: `revision` inserted in (c) → test_draft_extract_framing RED; one per-trait count,
  the 2,755, one oriented sha256 character, the total 13 → tests 3, 4, 5, 6 RED respectively.
- RED: tests 1-2 against the pinned table (`$Q8/red_15_8a4_t12.txt`: (c) 22,684 != 22,927; source sha256); tests 3-6
  against the pre-edit DRAFT (`$Q8/red_15_8a4.txt`, 4 failed).
- DRAFT (a4/draft_15_8a4.py 2099709 83 83; old → new in a4/draft_oldnew.txt; each old string unique): (a0) (c) inputs
  parenthetical; (a) the 8 oriented sha256 after the inputs list; (b) the collection clause (722,928 rows over 31
  regions; 162,724 lost keys = 159,969 restored by orientation + 2,755 not fitted); (c) the orientation step (159,969
  rows: asthma EUR 2,412, asthma AFR 3,798, BMI EUR 0, hypertension EUR 34,871, stroke EUR 36,195, stroke AFR 27,126,
  type 2 diabetes EUR 0, type 2 diabetes AFR 55,567; A/T and C/G 28,637, dropped from the fits by the allele-aware
  panel join, kept by the all-variant A1; 31 of 31 catalogs byte-identical); (d) (i) names the step; (e) the
  measured-counts row appends the oriented-input eligibility (total 13; pre-LD 83/83). test_amendment_text and
  test_prelock_pilot_fits green (30 passed, 2 skipped = FINAL / PUBLIC absent, as before).
- For Carter (not a DRAFT edit; the plan does not cover it): 15.8a2 EAF diagnostic
  (manifests/sumstats_r4_orientation_eaf.tsv). asthma EUR flipped rows: median |ΔEAF| 0.027 vs 0.005 unflipped; 19 of
  225 above 0.2, 14 of them indels (the SNV subset: 204, 0.0225, 5). Every other file: flipped ≈ unflipped. No row is
  filtered by EAF.
- R2 (collector drops unaudited; 15.7j re-review): RESOLVED by 15.8a2-a4: audit (15.8a), sumstats oriented to the
  catalog (15.8a2), production reads them with the catalogs a fixed point (15.8a3), eligibility re-measured and the
  DRAFT states the step and the audit (15.8a4). For 15.8f's review row.
- FULL (Slurm 2100181, cascadelake c020n02, HEAD 8d8b7bb6, 2h34m): QUICK 887 P / 2 S; HEAVY 340 P / 5 S; PINS 39 P;
  FULL 2,728 = 2,675 P / 53 S / 0 F (full_15_8a4.xml, sha256 a6f2132b…5567). check_15_8a4.py vs full_15_8a3.xml
  (2,722 = 2,669 P / 53 S, read from the file): 0 removed, +6 (all passed), 0 outcome changes, declared none, totals
  2,728 / 2,675 / 53 / 0, CHECK PASS (check_15_8a4.txt); NC (base as new) CHECK FAIL rc 1 (check_15_8a4_nc.txt).
  tests/m3/sparse_parent_benchmark.tsv clean.
- No production fit, no OSF, no lock; decision_rules.yaml locked: false, n_regions_min 7. NOT PUSHED. NEXT = 15.8b.

## 2026-11-26 — W3f 15.8b (R6: libopenblas pinned in envs/r_coloc.yml + exact pin file + job env lock manifest; job guard `--blas-pinned` for the five r_coloc rules; DRAFT (k); Carter Q-157J, Q-158R6S, Q-158R6G A, Q-158KW; no fit; no push)

- Commits (local): e47b6a83 (Task 1 locator conda_job_env.job_env_dir == Snakemake Env.address), cd96833e (Q-158KW gated,
  DEC-2026-11-26-ta-r4-draft-k-blas-wording, plan as executed), b113fcba (Task 2 pin + pin file + env lock manifest),
  e852040a (Task 3 guard), 99949f41 (Task 4 rule_gate), c54f6412 (Task 5 step 1 DRAFT (k)), 3e37c63a (D-11 fix), plus
  the records commit. Earlier: 4e47c20d (Q-158R6G gated + DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only, by the
  executor of the earlier plan version). That executor's out-of-order pin + guard commit caa5e6e3 was reverted in
  5ee7efe0. Its evidence is archived in `$Q8/b/prior_caa5e6e3/` (MANIFEST.txt) because it was produced before the
  build-before-wiring order. None of it is evidence for this run.
- Task 1 (Slurm 2101499, c020n02 Cascade Lake): the measured job env 0f343627…_ loads libopenblas 0.3.32; corename
  measured (blas_measure_15_8b.txt). Locator NC 0 (realpath(prefix) dropped from the hash) makes test 8 fail (2104875).
- Order: the env was built and proven identical BEFORE any guard code. Env D 516ec209…_ was built from the pin file
  (Slurm 2104927; "Using pinnings from", no "Failed to install"; `.pin.txt` sibling cmp-equal; no `.yaml` sibling).
  IDENTITY_OK: 222/222 URL#md5, libopenblas .so sha256 f1424288…572b, R library 144/144. Identity NCs (i)-(iv) each
  IDENTITY_DIFF on their own check. Shared cache /rs1/…/conda_pkgs 2188 entries, sorted-ls sha256 38c1cf64…f0d1
  before == after (CACHE_UNCHANGED). Old env 0f343627…_ kept.
- Guard (Task 3, Slurm 2105573 RED, 2105815 green 45 passed + NC 11): with `--blas-pinned` it refuses another BLAS
  (conda-meta record count/version, libblas/liblapack symlinks, runtime version token, Rscript, R-reported BLAS).
  Without it, the guard reads no BLAS and records `checked.blas_pinned: "not_checked"` and `blas.reason`. 16 NCs t3-1…t3-11,
  each FAILED-AS-REQUIRED.
- Flag derivation (Task 4): rule_gate takes `--blas-pinned` from workflow.get_rule(rule).conda_env (is_r_coloc_env).
  The truth source is Snakemake's own parse (tests/ta_r4/fixtures/rule_conda_envs.py, no rule_gate call); the dry-run
  `conda-env:` source was disproved (2104600, stop_15_8b_t3.txt). Measured partition 5/2 on the real and gate repos,
  porcelain equal before/after (2106577). Flagged: r4_run_finemap, r4_coloc_pair, r4_coloc_A1, r4_sim, r4_qtl_group.
  Unflagged (not_checked): r4_qtl_aggregate, r4_qtl_tiers. RED 2106800 (12 F / 40 P); green 2106819 52 passed;
  NCs t4-12…t4-17 each fail as required.
- Track B / m3: 23 rules outside ta_r4 use envs/r_coloc.yml. `.snakemake/conda` has 0 staged yamls. bin/setup-envs.sh's
  phase-2 fallback solves staged yamls, not the pin file. Track B and m3 rebuild this env on their next run from the pin
  file at libopenblas 0.3.34.
- DRAFT (k) (c54f6412): NEW_CLAUSE and NEW_SENTENCE extracted from the Q-158KW reply file (draft_k_15_8b.py), each
  delimiter/anchor count 1, each string once afterwards.
- FULL 1 (Slurm 2106909, HEAD c54f6412): 2,744 = 2,690 P / 53 S / 1 F; check_15_8b.py CHECK FAIL on one outcome change:
  test_storage_on_rs1::test_no_rs1_or_share_literals_in_r4_config_and_src passed -> failed. Cause:
  src/python/ta_r4/conda_job_env.py:10 `R4_CONDA_PREFIX = "/rs1/researchers/…"` (D-11 banned literal, e47b6a83).
  Reproduced by QUICK 2107067. Kept as full_15_8b_2106909_1F.xml (sha256 99ee5541…cfec9cc9) + check_15_8b_2106909_1F.txt.
- Deviation (orchestrator decision; Rule 1): 3e37c63a. The constant was removed and `job_env_dir(yml, prefix)` now
  requires the prefix. There is no src caller. bin/r4_fire.sh:13 stays the single source. New
  tests/ta_r4/fixtures/conda_prefix.r4_conda_prefix() does an exact match `^R4_CONDA_PREFIX=(\S+)$` and needs exactly
  one match, else RuntimeError. Callers: qtl_group_fixture, test_job_guard_blas (tests 8-11 + skip marker), the
  test_in_job_gate drift test. build_toy_workflow.py:218's own literal (c536547c) was left unchanged (not a
  job_env_dir caller, not in the D-11 scan). NCs (Slurm 2108827, fix_15_8b_2108827.out): pre-fix storage FAIL
  (2106909, 2107067); the helper raises on 2 and on 0 assignment lines (tmp copies) and returns the prefix on 1;
  locator NC 0 fails test 8 on the new signature (rc 1) and it passes after the md5-checked restore. QUICK 897 P / 2 S;
  guard + locator 54 passed.
- FULL 2 (Slurm 2108889, c022n03 Cascade Lake, HEAD 3e37c63a, 2h28m): QUICK 897 P / 2 S, HEAVY 346 P / 5 S, PINS 39 P; FULL 2,744 = 2,691 P / 53 S / 0 F (full_15_8b.xml,
  sha256 ac60ea0d…402d0b). check_15_8b.py vs full_15_8a4.xml (2,728 = 2,675 P / 53 S, read from the file): 0 removed, +16 all passed, 0 outcome changes, 11 declared passed -> passed, totals 2,744 / 2,691 / 53 / 0, CHECK PASS (check_15_8b.txt). Base for 15.8c = data/r4/tmp/w3f/q158/full_15_8b.xml.
- No production fit, no OSF, no lock; decision_rules.yaml locked: false, n_regions_min 7. NOT PUSHED. NEXT = 15.8c.
  Expected chain now: full_15_8b.xml 2,744 → 15.8c 2,752 → 15.8c2 2,758 → 15.8d 2,764 → 15.8e 2,766 → 15.8f 2,768.
