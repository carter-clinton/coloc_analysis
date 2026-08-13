# m3-04c Task 3 — PRE-FIRE GATE REVIEW

**The single current-state surface to read before deciding whether to fire the ~11-day /
$385–1,084 billed AoU loop.**

Anchor: commit `c4dc410` (2026-08-11 19:52:46 -0400), branch `m3-W2-aou-deltas` — check `L-01`.
Author: agent, `/gsd-quick` 260811-rcw. Cost of producing this document: **$0**.

---

## §0 — SCOPE STATEMENT (read this before the verdict)

**This document VERIFIES AND COLLATES. It fires nothing, decides nothing, and authorizes
nothing.**

* **Local evidence is a MEASUREMENT**, taken on **2026-08-11** at commit **`c4dc410`** (`L-01`).
  Every local claim below names the command that produced it; every one of those commands and
  its real, unedited output is on file beside this document in `260811-rcw-evidence.log`.
* **Perimeter state is LAST-KNOWN, not measured.** **ZERO perimeter contact was made in
  producing this document** — no `gsutil`, no `gcloud`, no `bq`, no `wb`, not even a read-only
  control-plane call; no cluster or VM was started, stopped, resumed or described. That is
  proven rather than promised: `grep -cE '^\$ .*(gsutil|gcloud|bq |wb )' 260811-rcw-evidence.log`
  returns **0**. Everything in §4 is therefore handed to Carter as a gate-time command **for him
  to run**, with its expected result stated.
* **Nothing outside this quick directory was modified.** `L-02` (before) and `L-20` (after) both
  show `git status --porcelain -- src tests config Snakefile` **EMPTY**.
* **The fire decision, and every gate-time action in §4 and §5, belong to Carter.**

---

## §1 — FIRE-READINESS VERDICT

**VERDICT:** All agent-verifiable preconditions GREEN as of 2026-08-11 at c4dc410; every remaining item is Carter's gate-time check or Carter's decision.

**What this verdict does and does not mean.** It is derived mechanically from
`260811-rcw-evidence.tsv`: all **20 of 20** rows carry verdict `PASS`, so the GREEN form is the
one the evidence licenses. It covers **only the agent-verifiable preconditions** — the suites,
the DAG, the config as shipped, the BLOCKER-1 read-path property, and the local data state.
It says **nothing** about the four perimeter facts in §4, which cannot be measured from NC State
and are last-known only; **nothing** about the PRE-FIRE decisions in §5, which are Carter's; and
**nothing** about the open items in §6, most of which do not block the fire but **bound what its
outputs may be used for** — BLOCKER-D above all. A GREEN line here is not a recommendation to
fire.

---

## §2 — CURRENT-STATE GATE TABLE

One table, reconciled across all four records. The "Evidence" column names the winning record
and its date, or the check id measured today.

| Gate | Current status | Evidence (command or artifact + date) | What would change it |
|---|---|---|---|
| **Panel reachability, Layer A** — curated→M2 crosswalk | ✅ **PRESENT AND CORRECT.** 12 rows; `SH2B3_12q24 → m2_region_00040__sub14`, `contained`, `overlap_frac` 1.000000; `BMI_Xq24` `unmapped` | `L-18` (measured 2026-08-11); crosswalk re-derivation recorded in HANDOFF `headline_2026_08_05b` | A 13th curated region added without a crosswalk rebuild (blast-radius L — drift is forward-only and WARN-only) |
| **Panel reachability, Layer B** — the `--ld-file` read path | ✅ **IMPLEMENTED AND ENFORCED.** `run_finemap`'s `shell:` passes `--ld-file {input.ld_matrix}` exactly once; the guard-rail `params.region_id` line survives character-for-character; the acceptance suite is green with all four behavioural tests **RUN, not skipped** | `L-11` = 1, `L-12` = 1, `L-13` 8 passed / 0 skipped (2026-08-11) | Any edit to `src/snakemake/rules/finemap.smk:449` or to `run_susie_rss.R`'s loader |
| **BLOCKER-A** — declared panel authoritative *at production thresholds* | ✅ **CLOSED** (quick-260805-23d, `51a60ca`+`ab19186`) | HANDOFF `gates.blocker_a_ld_file_authoritative` (2026-08-07); re-measured today: `L-14` 22 passed / **0 skipped**, incl. `test_thresholds_under_test_are_the_production_thresholds` | Changing `config/susie_policy.yaml` thresholds without re-running `L-14` |
| **BLOCKER-B** — Track-A EUR numerics containment | ✅ **CLOSED, END-TO-END.** The allow-list gates BOTH the crosswalk and `--ld-file`; off the list the declared file is invisible | HANDOFF `gates.track_a_eur_numerics` (2026-08-07); config as shipped re-read today: `L-07` `ancestries: ['AFR']` | Adding `EUR`/`TRANS` to `ld_read_path.ancestries`, **or** building `EUR_ukbb_pub` while that list is wider than `[AFR]` |
| **BLOCKER-C** — something builds the `.rds` | ✅ **CLOSED** as one operator command | HANDOFF `gates.blocker_c_nothing_builds_the_rds` (2026-08-07); re-measured today: `L-05` resolves a clean **575-job** DAG (276 + 276 + 1 + 22 = 575) | Nothing local. ⚠ Disclosed residual: `snakemake all` is still **not** self-sufficient |
| **BLOCKER-D** — `.npz`→`.rds` converter sizing | ◐ **PARTIAL — and this is the item that bounds what the money buys.** Only SH2B3 `__sub14` (22.8 GB) is convertible, on a big-memory node; MC4R (67.3 GB) and FTO/HLA (~553 GB) **fail fast** at the ceiling instead of OOM-killing | HANDOFF `gates.blocker_d_converter_oom` + `resume_on_reconnect` #3 (2026-08-07); ceiling re-read today: `L-09` `m3_convert_max_n_var = 120000` | A **sparse `.npz`** — i.e. a producer-side change to a frozen file (`plink_ld_to_npz.py`), which is exactly why it is not closed. See §6 |
| **Occlusion catalog refusal gate 1** — `allow_partial_manifest` | ✅ **ARMED, default-refuse.** **Not a config key at all**; the default is in code | `L-10`: absent from `config/pipeline.yaml`; code default `src/python/assemble_occlusion_catalog.py:345` `allow_partial_manifest: bool = False`; the GATE-1 raise at `:415` | Passing `--allow-partial-manifest` / `allow_partial_manifest=True` at STEP E |
| **Occlusion catalog refusal gate 2** — `allow_degraded` | ✅ **ARMED, default-refuse.** `occlusion_lockstep.allow_degraded = False` | `L-10` (measured 2026-08-11; the key is at `config/pipeline.yaml:295`, **not** the `:266` the m3-04c PLAN cites — see §2.1(7)); raise at `assemble_occlusion_catalog.py:460` | The PRE-FIRE 1b branch (iii) decision, which sets it `true` **in the same act** as a dated non-publication note |
| **Egress classification** (skill GATE 0) | ✅ **RULED PASS 2026-04-28** — institutional basis; aggregate stats over n≥60k AFR clear the n≥20 floor → standard per-file egress review at export time, not a per-data-class letter. ⚠ **LAST-KNOWN (dated record; not re-verifiable from NC State)** | `.claude/skills/aou-ld-pipeline/SKILL.md` §Wave 2 gate sequence; `.planning/amendments/aou-egress-audit-log.md` | Nothing pending. **This row survives the skill's staleness — see §2.1(3)**. **Fire-time re-verification NOT required:** it is an institutional ruling on a data class, not a mutable resource; nothing a fire does can change it, and STEP D re-enters per-file egress review anyway |
| **CDR pin + cost/credit** (skill GATE 1) | ✅ **CLEARED 2026-06-12** (CDR v8). ⚠ **LAST-KNOWN (dated record; not re-verifiable from NC State)** | same record | A CDR version change; `_resolve_aux_base` makes v8→v9 a no-op for path resolution. **Fire-time re-verification NOT required** for path resolution for that reason; the **cost/credit half is a live balance** and Carter should eyeball it in the Workbench billing panel before a $385–1,084 commit |
| **Cohort rebuild** (skill GATE 1.5) | ✅ **DONE + verified** (3 MTs, `cohort_summary` 3 rows). ⚠ **LAST-KNOWN (dated record; not re-verifiable from NC State)** | same record | Deleting the AoU VM or the cohort MTs. ⚠ **THIS ONE DOES NEED A GATE-TIME RECHECK** — the MTs are mutable perimeter state and the fire reads them. See the new §4 row 5 (added 2026-08-12, B-MEDIUM-4) |
| **Pre-registered 4-check validation protocol** | ⛔ **NEVER RUN.** Zero artifacts in all four `validation/check_*/` dirs. Check 2 was **REDEFINED** under an operator override | `L-19` = 0 (measured 2026-08-11); HANDOFF `gates.validation_4check`; `gates.osf_pre_registration` | Running it post-fire — and, for citation, the OSF amendment-update at STEP F |
| **Stale `gs://` panel TSV** (PRE-FIRE 2) | ❓ **PERIMETER-ONLY — UNKNOWN from here** | §4 row 3 | Carter's `gsutil stat` at gate time |
| **Manifest-egress gap** (PRE-FIRE 1) | ✅ **LANDED 2026-08-12 EVENING** (`5284505`, quick-260812-ox1 — the per-region upload this row's "what would change it" named; branch (i) is the live default; see Corrections #12). Row as written 2026-08-11: ⛔ OPEN, a Carter decision — the manifest has no path out of the perimeter | §5 PRE-FIRE 1; m3-04c PLAN :1322-1352; `260812-ox1-READY-TO-FIRE.md` item 7 | ~~Landing the per-region manifest upload as its own reviewed quick task, or accepting branch (iii)~~ — the first option was taken |
| **Real-`.bim` validation** (PRE-FIRE 3) | ❓ **PERIMETER-ONLY — and carries an OPEN index-origin question** | §4 row 4 | Settling 0- vs 1-based origin against the real `.bim` |
| **Region-1 re-run** (STEP A) | ⛔ **NOT RUN** — it is the gate immediately before the money | §5 STEP A | Carter firing region 1 only |
| **Suite health** | ✅ **GREEN, at baseline, skips exactly at the pinned values** | `L-03` 902 passed / 31 skipped / 0 failed; `L-04` 136 / 1 / 0 (both measured 2026-08-11) | Any new test landing as a SKIP — see §3 |
| **DAG health** | ✅ **GREEN** on the targeted convert target and on `--list` | `L-05` exit 0 / 575 jobs; `L-06` exit 0 | See §3 for why the full-workflow `--dry-run` is STRUCK and not run |

### §2.1 — DIVERGENCES BETWEEN THE RECORDS, STATED AND RESOLVED

Four records, four dates. Two contradict each other, one contradicts **itself**, and one
describes a producer that was killed. Every seam is shown; every winner is named; the rule is
**recency**, and where today's measurement corroborates the winner that is said explicitly.
Nothing below is silently merged.

**(1) `.planning/HANDOFF.json` contradicts ITSELF — its narrative gate rows are frozen at their
own writing dates.**
`gates.panel_reachability` still reads *"⛔ OPEN AND DEEPER THAN DIAGNOSED … CARTER'S DECISION"*
and `gates.blocker1_ld_read_path` reads *"✅ DECIDED … ⛔ NOT YET IMPLEMENTED"* — both frozen at
**2026-08-04/05**. Within the **same file**, `blast_radius_gate_ledger` (*"the ~11-day billed
fire: CLEAR on A/B/C"*), `blocker_a_ld_file_authoritative` (*"✅ CLOSED"*),
`blocker_c_nothing_builds_the_rds` (*"✅ CLOSED"*) and `completed_this_session` are current as of
**2026-08-07**.
→ **WINNER: the 2026-08-07 ledger rows, by recency.** ✅ **Corroborated by measurement today**,
which is stronger than recency alone: `L-11`/`L-12` show the `--ld-file` threading and its guard
rail present in `finemap.smk`, and `L-13`/`L-14` show both enforcing suites green. "NOT YET
IMPLEMENTED" is **false today**.

**(2) `.planning/HANDOFF.json` contradicts itself on the suite count.**
`gates.m3_04c` quotes *"Suite 548P/31S/0F"* (the **2026-08-05** snapshot); `suite_baselines` in
the same file says **902 / 31 / 0** (2026-08-07).
→ **WINNER: `suite_baselines`, by recency.** ✅ **Corroborated exactly by `L-03` today:
902 passed, 31 skipped, 0 failed.** The 548 figure is a historical snapshot and must not be
quoted as current.

**(3) `.claude/skills/aou-ld-pipeline/SKILL.md` §"Wave 2 gate sequence" DESCRIBES A PRODUCER THAT
WAS KILLED — but only partly, and throwing the whole table out would be the very error this
reconciliation exists to prevent.**

*Superseded (do NOT present these as live blockers):* the skill's **GATE 2 / GATE 3** are the
Hail `BlockMatrix` Path-A.3 fire — the A.3 lowering hang, **CR-01**'s ~2 TB dense-scratch
ordering question (A vs B), *"full 322-cell production + 44 egress"*, *"Egress = 44 export
requests (22 chr × 2 anc)"*, the atomic-final-write Phase 2, and the region set given as
*"322 = 161 M2 regions × 2 ancestries"*. That producer was **re-scoped away**.

*The current producer:* `src/python/run_native_ld_panel.py` — **native plink1.9, Hail-free**, ONE
stopped VM, **AFR-only**, **276 regions**, writing per-region `.npz` **directly** to
`gs://<bucket>/ld/AFR_aou/`. Egress is redefined to **at most 22 AFR chromosome groups plus
within-chromosome size splits** (`.planning/amendments/m3-egress-and-validation-protocol-addendum.md`
§(a), *"44 → at most 22"*). ✅ The 276 figure is corroborated today by `L-17`: **276 unique
`region_id`, 123 with `__sub`, 153 whole; 153 + 123 = 276 re-performed, not asserted** — and the
manifest's 552 rows are 276 × 2 ancestries, not 552 regions.

*Still LIVE and still VALID in that same skill table:* **GATE 0** (egress classification, RULED
PASS 2026-04-28), **GATE 1** (CDR pin v8 + cost/credit, CLEARED 2026-06-12) and **GATE 1.5**
(cohort rebuild, DONE). → **WINNER: split by row.** The skill is stale about the *producer* and
authoritative about the *institutional* gates.

**(4) `m3-04c-BLAST-RADIUS.md` §"Gate binding" vs HANDOFF's ledger, on what blocks the fire.**
The blast radius (**2026-08-05**) names **BLOCKER-A, BLOCKER-C and BLOCKER-D** as blocking the
~11-day fire. HANDOFF's `blast_radius_gate_ledger` (**2026-08-07**) records *"CLEAR on A/B/C;
⚠ BLOCKER-D PARTIAL"*.
→ **WINNER: HANDOFF (2026-08-07), by recency.** A and C were closed by quick-260805-23d; **D is
PARTIAL and remains a real bound on the deliverable** (§6).

**(5) ⚠ FOUND BY THIS RECONCILIATION — the two records give DIFFERENT BLOCKER-D magnitudes, and
the difference is exactly a factor of two.**
The blast radius (2026-08-05) says *"SH2B3 `__sub14` = 75,497 → **45.6 GB**; FTO/HLA = 363k–372k
→ **~1.1 TB**"* against `mem_mb=8000`. HANDOFF (2026-08-07) says **22.8 GB / 67.3 GB / ~553 GB**
with `mem_mb=64000` and a fail-fast ceiling.
→ **WINNER: HANDOFF, by recency** — and the seam is explained rather than papered over:
**re-performed here**, 75,497² × 8 bytes = 45.6 GB (float64) and × 4 bytes = 22.8 GB (float32);
372,000² × 8 = ~1.1 TB and × 4 = ~553 GB. The blast radius measured the **pre-remediation
float64** read; HANDOFF measures the **post-`57b381f` float32** read. **They are the same
regions, not two disagreeing measurements.** Both sets are consistent with `L-09`
(`m3_convert_max_n_var = 120000`): SH2B3's 75,497 clears the ceiling, MC4R (n ≈ 130k, from
67.3 GB ÷ 4 bytes) and FTO/HLA (363k–372k) do not, so they fail fast.

**(6) ⚠ FOUND BY THIS RECONCILIATION — the m3-04c PLAN contradicts the crosswalk that shipped.**
Task 3's acceptance criteria (PLAN `:1518`) say *"the `m2_region_00040__sub00` panel was ACCEPTED
at `SH2B3_12q24`"*. The **shipped** crosswalk maps SH2B3 to **`m2_region_00040__sub14`** (`L-18`,
measured today). `__sub00` is the **66 Mb off-target** id that the 2026-08-05b replan corrected
(HANDOFF `headline_2026_08_05b`: all 18 subregions of a split parent tie on the parent bounding
box, and the lexicographic tie-break returned `__sub00`).
→ **WINNER: the shipped crosswalk + `headline_2026_08_05b`.** §5 STEP A below uses **`__sub14`**.
Read PLAN `:1518` as a stale leftover, not as an instruction.

**(7) ⚠ FOUND BY THIS RECONCILIATION — a stale line number in the PLAN's PRE-FIRE 1b.**
It cites `allow_degraded` at `config/pipeline.yaml:266`; measured today (`L-10`) the key is
`occlusion_lockstep.allow_degraded` at **`:295`**. **The value is unchanged (`False`)** — only
the pointer moved. Named so nobody edits line 266.

**(8) ⚠⚠ FOUND BY THIS RECONCILIATION — THE OLDER RECORDS' LINE NUMBERS HAVE DRIFTED AS A CLASS,
including for the one gate STEP A asks Carter to reason about.** This is not a cosmetic
complaint: DEC-2026-08-05 already recorded that *"every `finemap.smk` line number in the m3-04c
plan is stale"* after m3-04b inserted 48 lines. The same rot has since reached other files.
**Every line number in this review was re-anchored against the tree at `c4dc410` before it was
written down.** The corrections:

| Cited by | Record's line | Measured today at `c4dc410` | Why it matters |
|---|---|---|---|
| the SuSiE quality gate `overlap >= MIN_LD_OVERLAP && coverage >= MIN_LD_COVERAGE` | m3-04c PLAN `:184`; blast radius `:216` | **`run_susie_rss.R:500`** (thresholds assigned at **`:716-718`**; the policy YAML is read at `:715`) | **STEP A sends Carter to read this gate.** Both prior pointers land on unrelated lines |
| `provenance_source` assigned as a scalar | m3-04c PLAN `:202` | **`assemble_occlusion_catalog.py:230`** | It is the guarantee that a MIXED provenance stamp is impossible |
| production varids are `chr:pos:ref:alt` on GRCh38 | m3-04c PLAN `:391-400` | **`run_native_ld_panel.py:507` — and that line is INSIDE A DOCSTRING** (the block runs `:498-511`) | It is what makes the degraded reconstruction recoverable at all. ⚠ **There is no code line in that file asserting the format**: `grep -n 'chr:pos:ref:alt' src/python/run_native_ld_panel.py` returns exactly one hit, `:507`, and it is prose. The varids are produced upstream by `hl.export_plink`, so the in-repo statement of this fact is documentation, not an enforced invariant. Cite it that way |
| the `gs://` upload set | m3-04c PLAN `:922-938` | `:922` (`if ok:`), uploads at **`:925-926`** / **`:929`** / **`:935-937`** | It is the proof the manifest is NOT uploaded |
| `allow_degraded` config key | m3-04c PLAN `:266` | **`config/pipeline.yaml:295`** | §2.1(7) |
| **CORRECTED 2026-08-12 (B-LOW-1):** the `occlusion_manifest.tsv` WRITE | **this review's own earlier text: `occlusion_manifest.py:203-208`** | **`append_region_manifest`: the append path is `:195-196` (`with manifest_path.open("a")` → `fresh.to_csv(fh, …, header=False)`); the fresh-file path is `:181` (`new.to_csv(manifest_path, …)`).** `:200-214` is `append_occlusion_rows`, whose `:203` is a keyword-argument default and whose `:204-212` are its DOCSTRING — the earlier `:203-208` pointed at documentation, not at a write | PRE-FIRE 1's whole argument is *"this file is written to local scratch and never uploaded"*. A reader following `:203-208` to check that claim lands in a docstring and cannot confirm it |
| **CORRECTED 2026-08-12 (B-LOW-1):** the `MIN_LD_*` threshold loads | **this review's own earlier text: `run_susie_rss.R:713-716`** | **`:716-718`** — `MIN_LD_OVERLAP` `:716`, `MIN_LD_COVERAGE` `:717`, `MIN_LD_MIN_USE` `:718`; `:715` is `policy <- yaml::read_yaml(opt$policy)` and `:713-714` are comments | The cited `:713-716` **excluded two of the three thresholds**, including `MIN_LD_COVERAGE`, which is half of the gate STEP A sends Carter to reason about |

→ **WINNER: the measured tree at `c4dc410`, in every row.** The underlying FACTS all survived —
the gate exists, the scalar assignment exists, the varid format is as described, the manifest
still is not uploaded. **Only the pointers were wrong.** Treat any line number quoted from a
record older than this review as needing re-anchoring before it is acted on.

**(9) ⚠ ADDED 2026-08-12 (B-MEDIUM-5) — the m3-04c PLAN CONTRADICTS ITSELF on which branch
admits `provenance_source == excludelist_degraded`, and a post-fire auditor would otherwise meet
it cold at STEP E.**

* PLAN `:1395` (inside PRE-FIRE 1b) says the acceptance criteria admit
  `provenance_source == excludelist_degraded` **ONLY under branch (iii)**; under (i)/(ii) it must
  be `stage_a_manifest`.
* PLAN `:1508` (inside the Task-3 acceptance criteria) says `excludelist_degraded` **under branch
  (ii) with `allow_degraded: true` visible in `config/pipeline.yaml`.**

These cannot both be true, and they name different flags. → **WINNER: `:1395`, the branch-(iii)
reading — because it is the one the CODE implements, re-measured at HEAD 2026-08-12:**

* `assemble_occlusion_catalog.py:230` — `df["provenance_source"] = provenance` is a **scalar**
  assignment, so a MIXED stamp is impossible by construction.
* **GATE 1** — `:415` `if orphaned and not allow_partial_manifest:` raising at `:416`. This is
  the **branch (ii)** state: a NON-EMPTY Stage-A rollup with some regions carrying an excludelist
  and no manifest. Its remedy flag is **`allow_partial_manifest`**, and the catalog it then emits
  is still stamped **`stage_a_manifest`** — `excludelist_degraded` is not reachable here.
* **GATE 2** — `:460` `if not allow_degraded:` raising at `:462`, reached only where
  `source = PROVENANCE_EXCLUDELIST_DEGRADED` has already been chosen at `:456` because the
  Stage-A manifests are **absent or empty entirely**. This is **branch (iii)**, and
  `allow_degraded` is its flag.

**The code-correct reading, to be applied at STEP E:** `excludelist_degraded` + `allow_degraded:
true` belongs to **branch (iii)** only. Under branch (ii) the correct flag is
**`allow_partial_manifest`** and the correct stamp remains **`stage_a_manifest`** with
`n_regions_excludelist_only` reported. **Read PLAN `:1508`'s "(ii)" as a typo for "(iii)"** — do
not let it license `allow_degraded` for a partial-manifest state, which would discard recoverable
provenance the OSF amendment-update commits to publishing.

---

## §3 — LOCAL RE-VERIFICATION (agent-verifiable, $0, NC State)

Rendered from `260811-rcw-evidence.tsv`; every command's real output is in
`260811-rcw-evidence.log` under the matching `##### L-NN` block.

| id | what | command | expected | observed | verdict |
|---|---|---|---|---|---|
| `L-01` | HEAD + date, the review's as-of point | `git log -1 --date=iso --format='%H %ad'` | record it | `c4dc410d0954ca6141cc9da2cee492681d2f187d 2026-08-11 19:52:46 -0400` | **PASS** |
| `L-02` | no source drift **before** the run | `git status --porcelain -- src tests config Snakefile` | EMPTY | (empty; exit 0) | **PASS** |
| `L-03` | `tests/m3` — ran **exactly once** | `… -m pytest tests/m3 -q` | 902 P / **31 S** / 0 F | `902 passed, 31 skipped, 4 warnings in 927.71s (0:15:27)` | **PASS** |
| `L-04` | `tests/phase2` | `… -m pytest tests/phase2 -q` | 136 P / **1 S** / 0 F | `136 passed, 1 skipped in 1.85s` | **PASS** |
| `L-05` | targeted convert DAG (BLOCKER-C) | `… snakemake --snakefile Snakefile m3_convert_aou_afr_rds_all -n --quiet` | exit 0, **575 jobs** | `build_ld_rds_aou_afr 276; m3_aou_npz_arrives 276; m3_convert_aou_afr_rds_all 1; m3_ingest_aou_export_arrives 22; total 575` | **PASS** |
| `L-06` | `--list`, the MEDIUM-7 substitute | `… snakemake --snakefile Snakefile --list` | exit 0 | exit 0; full rule list — **926** output lines, of which **148** are rule names (the rest are indented docstrings); verbatim in the log | **PASS** |
| `L-07` | `ld_read_path` as shipped | `python -c '… print(…["ld_read_path"])'` | `enabled/AFR/allele_aware/coloc` all set | `{'enabled': True, 'ancestries': ['AFR'], 'allele_aware': True, 'coloc': True}` | **PASS** |
| `L-08` | `strict_aou_only` | same load | `False` | `ld_panel.strict_aou_only = False` | **PASS** |
| `L-09` | BLOCKER-D ceiling — ⚠ **A CONFIG-VALUE READ ONLY** (annotated 2026-08-12, B-LOW-3) | same load | `120000` | `m3_convert_max_n_var = 120000` | **PASS** — ⚠ **this proves the VALUE is shipped, not that anything ENFORCES it.** The fail-fast enforcement lives at `src/snakemake/rules/m3_convert_npz_rds.smk:132` (read) → `:163` (`max_n_var=` param) → `:180` (passed as the R script's 4th argv) and `src/scripts/ld_npz_to_rds.R:272` (`if (n_input > max_n_var) stop(…LD_CONVERT_N_VAR_CEILING…)`). **The L-set does not measure any of that** |
| `L-10` | both refusal gates | same load + `grep` on the assembler | `allow_degraded False`; `allow_partial_manifest` **absent** ⇒ record the code default | `occlusion_lockstep.allow_degraded = False`; `allow_partial_manifest = ABSENT`; code default `assemble_occlusion_catalog.py:345`; GATE-1 raise `:415` | **PASS** |
| `L-11` | `--ld-file {input.ld_matrix}` **somewhere in `finemap.smk`** — ⚠ **A FILE-WIDE GREP, NOT A RULE-SCOPED ONE** (label corrected 2026-08-12, B-LOW-3) | `grep -c` on `finemap.smk` | exactly `1` | `1` | **PASS** — ⚠ the command proves the token occurs **once in the file**; it does **not** prove it sits inside `run_finemap`'s `shell:`. **The SCOPED proof is `L-13`'s `test_run_finemap_shell_passes_the_declared_ld_matrix` (`tests/m3/test_ld_read_path.py:251`)**, which parses the rule. Cite `L-13` for the property; cite `L-11` only for presence |
| `L-12` | the `params.region_id` guard rail, character-for-character | `grep -cF` on `finemap.smk` | exactly `1` | `1` | **PASS** |
| `L-13` | DEC-2026-08-05 acceptance suite | `… -m pytest tests/m3/test_ld_read_path.py -v` | 8 P / **0 S**, four behavioural tests RUN | `8 passed in 15.32s`, 0 skipped (roll-call below) | **PASS** |
| `L-14` | **production-threshold** acceptance suite | `… -m pytest tests/m3/test_ld_declared_authoritative.py -v` | all pass, **0 skipped** | `22 passed in 63.18s`, 0 skipped | **PASS** |
| `L-15` | `data/processed/ld_reference` | `test ! -e … && echo ABSENT` | `ABSENT` | `ABSENT` | **PASS** |
| `L-16` | banked AFR `.npz` locally — ⚠ **BLIND TO A MISSING DIRECTORY** (annotated 2026-08-12, B-LOW-4) | `ls data/interim/aou_ld_exports/AFR_aou/*.npz 2>/dev/null \| wc -l` | `0` | `0` | **PASS** — ⚠ **the `2>/dev/null` makes "the directory does not exist" and "the directory exists and is empty" print the SAME `0`.** For a pre-fire row expecting 0 that is harmless; **post-fire it is not** — after STEP D a `0` here could mean the exports landed somewhere else entirely. Re-run it without `2>/dev/null`, or `test -d` first, before reading a post-fire `0` as "nothing banked" |
| `L-17` | region ids, by header name | `python -c '… csv.DictReader …'` | 276 unique, 123 `__sub` | `552 rows; 276 unique; 123 __sub; 153 whole; 153 + 123 = 276 True; {'AFR': 276, 'EUR': 276}` | **PASS** |
| `L-18` | curated→M2 crosswalk | `python -c '… csv.DictReader …'` | 12 rows; SH2B3→`__sub14`/contained; `BMI_Xq24` unmapped | `12`; `m2_region_00040__sub14` / `contained` / `1.000000`; `unmapped` / `0.000000` | **PASS** |
| `L-19` | 4-check validation artifacts | `find …/validation -type f ! -name .gitkeep \| wc -l` | `0` | `0` | **PASS** |
| `L-20` | no source drift **after** the run | `git checkout -- …sparse_parent_benchmark.tsv; git status --porcelain -- src tests config Snakefile` | EMPTY | (empty; exit 0) | **PASS** |

**20 of 20 PASS. 0 FAIL. 0 RED.** There is therefore no RED block under this table. Had any row
been non-PASS it would appear here as a loud block, not as a footnote — and §1 would carry the
NOT-READY form instead.

**The skip-count rule, and whether it held.** The project's standing rule (HANDOFF
`suite_baselines`, verbatim): *"Skips must STAY at 31 and 1. A new test landing as a SKIP is NOT
evidence — check the skip count, not just the failure count."* **It held exactly**: `L-03`
observed **31** skipped and `L-04` observed **1** skipped. Neither drifted, so no skip-count
reconciliation is owed. The passed counts also landed exactly on the 2026-08-07 baseline
(902 and 136) — and the 15 commits between that baseline (`b02707a`) and this anchor touched
**0** files under `src/`, `tests/`, `config/` or `Snakefile` (log blocks `CONTEXT-A`,
`CONTEXT-B`), which is what a docs-only arc should look like.

**`L-13` behavioural roll-call, BY NAME.** *"8 passed"* alone is **not** sufficient evidence — a
suite that silently skipped its only behavioural assertions would print an equally green line.
All four ran:

| behavioural test (`tests/m3/test_ld_read_path.py`) | state |
|---|---|
| `test_loader_opens_the_declared_file_not_the_reconstructed_path` (`:306`) | **PASSED** |
| `test_absent_ld_file_still_reconstructs_from_ld_dir` (`:335`) | **PASSED** |
| `test_ld_file_works_when_ld_dir_is_absent` (`:356`) | **PASSED** |
| `test_both_absent_returns_the_byte_identical_legacy_status` (`:389`) | **PASSED** |

**A skipped behavioural test would not be evidence** — it is the absence of a measurement wearing
the colour of one ([[feedback_skip_guard_masks_not_fixes]]). The marker that makes these RUN
rather than skip is the `m3-r-ld` conda env at `/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld`;
do not delete it.

**The BLOCKER-1 acceptance property, and what each of its TWO enforcing suites does and does not
prove.** The property, verbatim from `DEC-2026-08-05-m3-ld-read-path`:

> *"prove resolved == what-the-script-opens — grep the rule's `shell:` for `{input.ld_matrix}`,
> then assert the R script opens that exact path. A green DAG is NOT evidence."*

* **`tests/m3/test_ld_read_path.py`** (`L-13`) is the DEC-2026-08-05 acceptance suite. It proves
  **WHICH FILE IS OPENED**. It **does not** prove acceptance-threshold behaviour, and it says so
  itself: its harness `source()`s only the function-definition prefix, cut above the point where
  `MIN_LD_*` are read from `config/susie_policy.yaml`, so it pins `MIN_LD_OVERLAP <- 1L`,
  `MIN_LD_COVERAGE <- 0.0`, `MIN_LD_MIN_USE <- 1L` at `:186-188` and documents the delegation at
  `:178-182`. ⚠ **The blast radius's sentence *"the gate is disabled in all 8 of them"* is TRUE
  OF THIS FILE and is NOT the current state of the property** — because of the second suite:
* **`tests/m3/test_ld_declared_authoritative.py`** (`L-14`) is, in its own words (`:3`),
  *"THE PRODUCTION-THRESHOLD ACCEPTANCE SUITE for the m3-04c blast radius."* It **READS** the
  thresholds — `min_ld_overlap: 50`, `min_ld_coverage: 0.5`, `min_ld_min_use: 10` — from
  `config/susie_policy.yaml` at `:78-83` (*"read, never hardcoded"*), exercises
  `assert_declared_ld_authoritative()`, and carries its own guard,
  `test_thresholds_under_test_are_the_production_thresholds`, plus **three**
  `test_negative_control_pre_change_*` tests (`:935`, `:1018`, `:1296` — **corrected 2026-08-12,
  B-LOW-2**; this review earlier said "four", and `grep -c` on the file measures **3**) that
  recover the pre-change loader and assert the **defective** outcome. It is the BLOCKER-A remediation (quick-260805-23d, `51a60ca`+`ab19186`).
  It ran green with **0 skipped** today.
* ⚠ One precision the records blur: `test_ld_read_path.py:181-182` delegates thresholds to
  `test_finemap_loader_contract.py`, while the suite that actually owns the **blast-radius**
  production thresholds is `test_ld_declared_authoritative.py`. Both exist; the delegation
  comment names the older one.

**`L-05` vs `L-06` — the distinction a reader who knows MEDIUM-7 will otherwise trip on.**
`L-05` is the **TARGETED** `m3_convert_aou_afr_rds_all` dry-run. It **is satisfiable** and it
**was run** (exit 0, 575 jobs). It is **not** the FULL-WORKFLOW `snakemake --dry-run --quiet`,
which is **STRUCK as unsatisfiable pre-fire** (D-04b-03 / MEDIUM-7): `data/processed/ld_reference/`
does not exist (`L-15` = `ABSENT`), so `resolve_ld_path` **raises**. `snakemake --list` (`L-06`)
is its accepted substitute. **No struck check was run, and nothing was fabricated to make a check
pass** — `L-15` and `L-16` *expect* absence, so there was nothing to manufacture; no fake `.rds`
was touched and no absent data directory was created.

---

## §4 — WHAT CANNOT BE VERIFIED FROM HERE (perimeter-only)

Every row is **LAST-KNOWN**, not a current measurement. The commands are **instructions for
Carter**, to be run **in-perimeter**. No agent ran any of them; none may.

| Fact | Last known (+ date + source) | Carter's gate-time command (in-perimeter) | Expected result |
|---|---|---|---|
| Bucket `.npz` count | **0/276** — 2026-08-07, HANDOFF `data_state` (*"AoU AFR native-plink LD panel does NOT exist: bucket .npz = 0/276"*) | **PRIMARY (literal bucket):** `gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz \| wc -l` — **alternate (env form, quoted):** `gsutil ls "${WORKSPACE_BUCKET}/ld/AFR_aou/"*.npz \| wc -l`. ⚠ **`WORKSPACE_BUCKET` ALREADY CONTAINS `gs://` — NEVER PREFIX IT.** `gs://${WORKSPACE_BUCKET}/…` double-prefixes: gsutil errors to **stderr**, stdout is **empty**, and `wc -l` prints **0** — which would FALSE-PASS this very row and read a healthy fire as dead. Corrected 2026-08-12, B-BLOCKER-1 | **0** pre-fire. Anything > 0 means a prior fire banked regions — reconcile before re-firing (`force_fresh=False` on resume). ⚠ **Post-fire, 276 is NOT a pass bar** — see the liveness-arbiter block below |
| VM state | **STOPPED, not deleted**; `n1-standard-32`; holds `/home/jupyter/afr_cohort` — 2026-08-07, HANDOFF `cluster` | Read the **AoU environment panel** in the Workbench UI (do not shell out) | Environment present, stopped, disk intact. ⚠ **READ THE DISK-TYPE LABEL BEFORE ANY DESTRUCTIVE ENV ACTION** — an AoU env on a **STANDARD** disk loses everything on delete; this project's rule is **Reattachable persistent disk** |
| The stale `gs://` panel TSV (PRE-FIRE 2) | **UNKNOWN** — never measured; the last relevant record is that the June/July fires appended `status=error` rows unconditionally (m3-04c PLAN `:1400-1406`) | `gsutil stat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv`; if present, `gsutil cat gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv \| head -1`. ⚠ Same never-prefix rule as row 1 if you use `${WORKSPACE_BUCKET}` instead. **URI derived at HEAD 2026-08-12, not guessed:** `run_native_ld_panel.py:122` `_DEFAULT_PANEL_NAME = "m3-W2-native-plink-panel.tsv"`, joined at `:734` as `_gs_join(gs_out_dir, _DEFAULT_PANEL_NAME)` with `gs_out_dir = str(out_dir)` (`:732`) = the `--out-dir` value, which the module docstring `:69,:72` gives as `gs://<bucket>/ld/AFR_aou`; the bucket is `SKILL.md:12,:43` | **9 tab-separated columns**, with `n_dropped_occluded` at `_PANEL_COLUMNS` **index 7** (re-derived today with `ast` — log block `CONTEXT-C`; a naive comma-split on that source is WRONG, the list carries commas inside comments). Otherwise `gsutil rm`. ⚠ **"0/276 banked" does NOT evidence the TSV's absence**: the `.npz`, not the TSV, gates the resume skip, and prior fires appended `status=error` rows unconditionally |
| The real-`.bim` validation (PRE-FIRE 3) | **UNKNOWN** — never run. ✅ **The index-origin question is SETTLED CODE-SIDE 2026-08-12 EVENING** (quick-260812-ox1; Corrections #13): the gated test computes BOTH sides in the same 0-based `enumerate` space, so an origin error fails LOUDLY and cannot false-pass — **the gated test is the instrument; the manual comparison this row prescribed is FORBIDDEN** (`260812-ox1-READY-TO-FIRE.md` item 8) | ⚠ **NO RUNNABLE COMMAND IS GIVEN HERE, AND THAT IS THE HONEST STATE** (corrected 2026-08-12, B-MEDIUM-3). The earlier "Byte-check …" wording wore the shape of an instruction without being one. The exact command **cannot be written from NC State**, because it must name the real cohort `.bim` produced in-perimeter, whose path is fixed at cluster build time and is not recorded on this side. **In-perimeter: place the real region-1 window `.bim` at `data/aou/region1_window.bim` and run the gated test by name** (runbook item 8) | Exactly the five expected region-1 ids at **1980475, 5733487, 5922718, 7492693, 8375822**. The 2026-08-11 "OPEN AND UNRESOLVED: the 0- vs 1-based index origin" clause is superseded per the status column — the off-by-one false-pass risk belonged to a MANUAL comparison, which is now forbidden |
| Region-1 re-run result (STEP A) | **NOT RUN** | See §5 STEP A | `.npz` 0 → 1; `status == ok`; `n_var` slightly under 102,421; `n_dropped_occluded` ≈ 5; no *"not symmetric"*, no *"Killed"*, no dmesg OOM |
| **Row 5 (ADDED 2026-08-12, B-MEDIUM-4) — the cohort MTs still hold DATA** | **DONE + verified, 2026-06 record** (3 MTs, `cohort_summary` 3 rows) — **last-known, and it is MUTABLE perimeter state the fire reads** | Per the skill's **invariant 1**, at the DATA layer and not on a marker: `gsutil du -s gs://rw-migration-aou-rw-476cdac2/ld/mt_AFR_qc.mt/entries/rows/parts/` **and** `count_cols()` / `count_rows()` off the MT itself. ⚠ Canonical path has **no `/mt/` subdirectory**; a wrong `…/ld/mt/…` path mimics the empty-final catastrophe | `du` **≫ 1 GB** and non-zero cols/rows. ⚠ **A `_SUCCESS` marker is NOT evidence of data** — the 2026-05-21 empty-MT ($2,100) and the 2026-06-10 empty-final catastrophes both passed a `_SUCCESS` check over 0 bytes. Firing 263 VM-h against an emptied MT is exactly that failure mode with a bigger bill |

> ### ⚠ THE LIVENESS ARBITER FOR THE FIRE
>
> **Liveness is the GCS `.npz` OBJECT LISTING climbing toward 276.**
>
> **NOT the kernel light. NOT a `_SUCCESS` marker. NOT the log.**
>
> The project's reason, learned the expensive way: **`_SUCCESS` is written on driver-side task
> accounting, not on contents validation** — a `_SUCCESS` over empty output is a state this
> project has actually produced. A lit kernel proves a process is attached, not that work is
> landing. Poll the object listing.
>
> **THE POLL COMMAND (corrected 2026-08-12, B-BLOCKER-1). PRIMARY FORM — literal bucket:**
>
> ```
> gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l
> ```
>
> **Alternate, env-variable form — note where the quotes go:**
>
> ```
> gsutil ls "${WORKSPACE_BUCKET}/ld/AFR_aou/"*.npz | wc -l
> ```
>
> ⚠⚠ **`WORKSPACE_BUCKET` ALREADY CONTAINS `gs://` — NEVER PREFIX IT.**
> `SKILL.md:43` requires `echo $WORKSPACE_BUCKET` to print `gs://rw-migration-aou-rw-476cdac2`.
> So `gsutil ls gs://${WORKSPACE_BUCKET}/…` expands to `gs://gs://…`: gsutil writes a usage
> error to **stderr**, prints **nothing** to stdout, and `wc -l` returns **0**. That zero is
> indistinguishable from "no objects" — it FALSE-PASSES the pre-fire "expected: 0" row above,
> and during STEP B it reads a **healthy fire as dead**. This is the same defect class the
> project already fixed once, in **quick-260611-tbw** (`fix-aou-2-workspace-bucket-double-prefix`,
> gap C3). The producer path itself is verified correct: `run_native_ld_panel.py:925-926`
> uploads to `{gs_out_dir}/{region_id}.npz` with `gs_out_dir` = the `--out-dir` value
> (`:732`), i.e. `gs://<bucket>/ld/AFR_aou/`.
>
> ⚠ **276 IS NOT A PASS BAR.** The m3-04c PLAN says so in as many words (`:1503-1504`):
> *"Do NOT hardcode 276 as a pass bar before the fire has run: a partial bank is a real,
> reportable outcome, not a failure to be papered over."* The producer makes a partial bank
> the EXPECTED shape of a bad region, not an exception: a region whose content verification
> fails is stamped `status="verify_failed"` (`run_native_ld_panel.py:917`) and the upload block
> is gated on `if ok:` (`:922`), so **a verify-failed region NEVER uploads** and the `.npz`
> listing simply does not advance for it (`:939-940` leaves it in scratch); and any exception
> is caught per region at `:943-945`, recorded as `status="error: …"`, and **the loop
> continues**. A count below 276 is therefore a RESULT TO REPORT with its per-region statuses,
> not automatically a failure — and a count that stops climbing is the signal to investigate,
> not a number to wait out.

---

## §5 — THE CARTER-ONLY SEQUENCE

**Cost band: ~263 VM-h, ~11 days, $385–1,084.** (Re-performed: 263 ÷ 24 = 10.96 ≈ 11 days.)

> ## ⛔ AN AGENT MUST NEVER FIRE THIS. It is Carter's terminal gate.
>
> This is a standing project rule (`.planning/HANDOFF.json` `do_not[0]`), not a scoping
> preference for this document. Nothing in this review authorizes it.

Faithful to m3-04c Task 3 (PLAN `:1302-1536`). **Gate precondition: do not fire until Tasks 1a,
1b, 1c and 2 have merged** — before them the fire produces a panel the fine-mapping DAG cannot
read. (`L-11`/`L-12`/`L-13`/`L-14` are the local evidence that they have.)

### PRE-FIRE 1 — the occlusion manifest has NO PATH OUT of the perimeter (HIGH; decide before firing)

> ✅ **SUPERSEDED 2026-08-12 EVENING — THIS RECOMMENDATION WAS TAKEN AND LANDED.**
> quick-260812-ox1 (`5284505`) implemented exactly the "LOWER-RISK OPTION,
> PREFERRED" below: a per-region `{region_id}.occlusion_manifest.tsv` uploaded
> inside the `if ok:` block, TDD with every assertion observed red, verifier 9/9.
> The gap this section describes is CLOSED; **PRE-FIRE 1b branch (i) is the live
> default** and the operative decision surface is `260812-ox1-READY-TO-FIRE.md`
> item 7. The section body is preserved below as the record of the analysis.
> (Corrections #12.)

`run_native_ld_panel.py:822` calls `ocm.append_occlusion_rows(...)`, which writes
`{compute_dir}/occlusion_manifest.tsv` (the write itself is `occlusion_manifest.py:195-196` on the
append path and `:181` on the fresh-file path, both inside `append_region_manifest`, which
`append_occlusion_rows` tail-calls at `:214` — **corrected 2026-08-12, B-LOW-1**; the previously
cited `:203-208` is that function's keyword default plus its docstring, not a write); in
`gs://` mode `compute_dir` is **LOCAL SCRATCH** (`:733`), and the upload set — inside the
`if ok:` at `:922`, with the three uploads at `:925-926` (`.npz`), `:929` (`.afreq`) and
`:935-937` (`.occluded.excludelist`) — is **only** those three. **The manifest is never uploaded
and dies with the scratch / VM.**

*What IS and is NOT lost without it.* The **lockstep still works**: production varids are
`chr:pos:ref:alt` on GRCh38 (`:507`), so `chr` and `pos_grch38` are recoverable from the
excludelists, which **are** uploaded — that is what m3-04b's degraded reconstruction path is for.
What is **NOT** recoverable: the **occluder attribution, the REF spans,
`occluding_deletion_ref_len`, and the reason/order labels** — precisely the per-drop provenance
the OSF amendment-update (osf.io/az52u, file `trsx5`) **COMMITS TO PUBLISHING**. This is a
**pre-registration compliance item, not a mechanics item.**

*Recommendation:* land it as its own reviewed `/gsd-quick` **before** the fire, uploading inside
the existing `if ok:` block alongside the excludelist. *Risk, stated honestly:*
`occlusion_manifest.tsv` is ONE file appended to by EVERY region; a bare overwrite races nothing
on a single serial VM but would race under any future sharded fan-out, and the P3 lesson
(`ff8cc47`) is that one upload helper serving two callers with opposite failure-safety needs
silently destroyed banked provenance. **LOWER-RISK OPTION, PREFERRED: upload a per-region
`{region_id}.occlusion_manifest.tsv`** so no object is ever overwritten — `aggregate_manifests`
already expects a LIST, and m3-04b's catalog rule already globs them.

### PRE-FIRE 1b — ⚠ THE `allow_degraded` DEAD-END. Decide and RECORD it, in writing, BEFORE firing

There are **TWO INDEPENDENT REFUSAL GATES**, both default-refuse, both verified armed today
(`L-10`):

* **GATE 1 — `assemble_occlusion_catalog.py:415` (raise body through `:434`), `allow_partial_manifest`
  (default `False`, in CODE at `:345` — it is *not* a config key).** Raises when the Stage-A
  rollup is NON-EMPTY but some regions have an excludelist and **no** manifest.
* **GATE 2 — `assemble_occlusion_catalog.py:460`, `allow_degraded` (default `False`;
  `config/pipeline.yaml:295`).** Raises when the Stage-A manifests are absent or empty entirely.

STEP E says only *"re-run the catalog rule"*, and **nothing flips either flag**. So the post-fire
state can **dead-end STEP E**: catalog missing → both filter rules blocked → every AFR
`run_finemap` blocked — **discovered after ~$385–1,084 and ~11 days.**

The fail-loud design of BOTH gates is **CORRECT and must not be softened into a silent
fallback.** What is required is a RECORDED decision covering **THREE** reachable states, not two:

* **(i) PRE-FIRE 1 LANDS AND EVERY REGION BANKS A MANIFEST (preferred).** Both flags stay
  `false`; the catalog is stamped `stage_a_manifest`; nothing else changes.
* **(ii) PRE-FIRE 1 LANDS BUT SOME REGIONS STILL LACK A MANIFEST.** ⚠ **This state is LIVE even
  under branch (i)**: `run_native_ld_panel.py:821-831` treats the per-region Stage-A append as
  **BEST-EFFORT and continues on any exception while still writing the excludelist.** GATE 1
  fires. Correct response: supply the missing manifests if recoverable; **only** if not, set
  `allow_partial_manifest: true` explicitly and record which regions are knowingly omitted
  (reported as `n_regions_excludelist_only`).
* **(iii) PRE-FIRE 1 IS DECLINED.** GATE 2 fires. Set `allow_degraded: true` **in the same act**,
  with a dated note stating explicitly which pre-registered provenance (occluder attribution, REF
  spans, `occluding_deletion_ref_len`, reason/order labels) will **NOT** be published, and
  confirming the drop-set itself is still correct.

**Write the chosen branch down BEFORE STEP B, and RE-READ it at STEP E** — **branch (ii) can only
be diagnosed after the fire**, so the gate must be re-entered rather than assumed settled.
`provenance_source == excludelist_degraded` is admissible **only** under branch (iii); under
(i)/(ii) it must be `stage_a_manifest`. Mixed is impossible by construction
(`assemble_occlusion_catalog.py:230` assigns `df["provenance_source"] = provenance` as a scalar
— the m3-04c PLAN's `:202` is stale, see §2.1(8)) and must never be silently accepted.

### PRE-FIRE 2 — rotate the stale `gs://` panel TSV (zero risk, zero compute cost)

See §4 row 3 for the command and the 9-column / index-7 expectation.

### PRE-FIRE 3 — the gated real-`.bim` validation

See §4 row 4. ✅ *2026-08-12 EVENING:* the 0-vs-1-based index-origin question is
**settled code-side** (the gated test is origin-safe; manual comparison forbidden)
— follow `260812-ox1-READY-TO-FIRE.md` item 8, not the older "settle it first"
instruction that stood here.

### STEP A — REGION-1 RE-RUN GATE

Re-run **region 1 ONLY**. **PASS** = `.npz` count 0 → 1, panel `status == ok`, `n_var` slightly
under 102,421, `n_dropped_occluded` ≈ 5 logged, no *"not symmetric"*, no *"Killed"*, no dmesg
OOM. **FAIL → stop and report; do not proceed to 276.**

⚠ **ALSO CHECK HERE: the SH2B3 coverage risk (MEDIUM-6).** The crosswalk maps `SH2B3_12q24` to
**`m2_region_00040__sub14`** (`L-18`; the earlier `__sub00` was 66 Mb off target — §2.1(6)).
`__sub14`'s WINDOW fully contains the curated interval and its CORE owns 523,169 of 600,000 bp
(87.2%); the remaining 12.8% lies in `__sub15`'s core and is covered only through `__sub14`'s
buffer. **But** `run_susie_rss.R:500` gates on **VARIANT**
`overlap >= MIN_LD_OVERLAP && coverage >= MIN_LD_COVERAGE` (**50** and **0.5**, loaded from
`config/susie_policy.yaml`; the three assignments are at **`:716-718`**, the policy read at
`:715` — **corrected 2026-08-12, B-LOW-1**; the previously cited `:713-716` excluded
`MIN_LD_COVERAGE` `:717` and `MIN_LD_MIN_USE` `:718`) — a realized variant-membership property,
**NOT** a bp property. ⚠ **Both older records point at the wrong line for this gate** — the m3-04c PLAN says
`:184` and the blast radius says `:216`; measured today it is `:500`. See §2.1(8).

Once `m2_region_00040__sub14` is banked, run one `run_finemap` for an AFR trait at `SH2B3_12q24`
and read the `estimate_s` log line: it prints `ld_matrix` (the path **OPENED**) and
`ld_file_declared` (the path **DECLARED**). **If `ld_matrix` reads `identity`, the coverage gate
rejected the panel** — report it with the observed `ld_overlap` / `ld_overlap_fraction`; **do not
paper over it.** The honest remedies are: select `__sub15` instead (it also fully contains the
locus), use the STITCHED parent `m2_region_00040` if one is built, or lower `min_ld_coverage`.
**All three are scientific calls, not executor calls.**

⚠ **The blast radius's correction, carried forward:** the SH2B3 **core straddle is a NON-RISK** —
the panel is computed over the **WINDOW** (`run_native_ld_panel.py:727-728`), `start_grch38 ==
window_start_grch38` for all 552 manifest rows, and the crosswalk's own `overlap_frac` is
**1.000000** (`L-18`). **No variant is missing**; the 12.8% is core bookkeeping.

### STEP B — THE FIRE (~263 VM-h, ~11 days, **$385–1,084**)

`nohup` plus `timeout 312h` (a 13-day wall-cap above the ~11-day estimate), **server-side**, on
the STOPPED-not-deleted Cloud Analysis VM. **Liveness is the GCS `.npz` object listing climbing
toward 276 — not the kernel light, not a `_SUCCESS` marker, not the log.** **Do NOT restart the
kernel.** Check in **every 2–3 days**. **Teardown is UI-only** (the in-perimeter pet SA has
list-only Dataproc permissions), so there is no self-delete; the `timeout` wall-cap is the
backstop.

**THE POLL COMMAND, at the point you will actually run it (corrected 2026-08-12, B-BLOCKER-1).
PRIMARY FORM — literal bucket:**

```
gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l
```

**Alternate, env-variable form — note where the quotes go:**

```
gsutil ls "${WORKSPACE_BUCKET}/ld/AFR_aou/"*.npz | wc -l
```

⚠⚠ **`WORKSPACE_BUCKET` ALREADY CONTAINS `gs://` — NEVER PREFIX IT.** `gs://${WORKSPACE_BUCKET}/…`
expands to `gs://gs://…`; gsutil errors to stderr, stdout is empty, `wc -l` prints **0**, and a
**healthy fire reads as dead**. Same defect class as quick-260611-tbw gap C3. If a poll ever
returns 0 after the fire has been running, **re-run it in the literal-bucket form before
concluding anything** — and check stderr, which `| wc -l` discards.

⚠ **276 IS NOT A PASS BAR** (m3-04c PLAN `:1503-1504`). A `status="verify_failed"` region never
uploads (`run_native_ld_panel.py:917` stamps it, `:922`'s `if ok:` gates the upload, `:939-940`
leaves the file in scratch), and the per-region `except` at `:943-945` records
`status="error: …"` and **continues the loop**. So a final count under 276 is **a partial bank —
a real, reportable outcome** to be reported with its per-region statuses, not a failure to paper
over and not a reason to re-fire blindly (`force_fresh=False` on resume).

### STEP C — SIZE AND PLAN THE EGRESS

`gsutil ls -l` over `ld/AFR_aou/*.npz` → a `region_id, chr, bytes` TSV →
`python src/python/plan_ld_egress.py` → `.planning/amendments/m3_egress_plan_AFR.tsv`. Expect
**at most 22 chromosome groups plus size splits**. ⚠ **Confirm the REAL AoU egress threshold on
the FIRST request — 50 GB is OUR working ceiling, not AoU's documented cap.**

### STEP D — EGRESS TO NC STATE, PER GROUP

File the AoU egress request per group; `gsutil -m cp` the group's object URIs into
`data/interim/aou_ld_exports/AFR_aou/`; **also** fetch the `.occluded.excludelist` files, the
`.afreq` sidecars, the panel TSV, and — if PRE-FIRE 1 landed — the occlusion manifest(s). Append
one row per group to `.planning/amendments/aou-egress-audit-log.md` under
`## Per-Bundle Audit Entries` with the Q12 schema, plus a per-group **SHA-256 sub-manifest**
under `.planning/amendments/sha256/`. Commit per group with token `(m3-04c-T3-chr{N}-AFR)`.

### STEP E — HAND BACK TO THE DAG

Re-run m3-04b's catalog rule **under the branch RECORDED at PRE-FIRE 1b** (re-read it now — see
branch (ii)): it assembles the REAL catalog and the lockstep filter stops being a no-op. Then run
the per-chromosome ingest flags and the `.npz` → `.rds` conversion (`L-05`'s 575-job DAG). ⚠ Only
the BLOCKER-D-convertible subset will convert — see §6.

### STEP F — OSF AMENDMENT-UPDATE FOR THE CHECK-2 REDEFINITION

`.planning/amendments/m3-egress-and-validation-protocol-addendum.md` redefines a **PRE-REGISTERED
hard gate** (AOU-LD-PIPELINE.md §9). **Agent DRAFTS, Carter POSTS** to osf.io/az52u, and the file
GUID is recorded in-repo — the m3-07a discipline. **No redefined check may be cited as PASSED
before that posting is recorded.** Do not re-post or EDIT the BODY of any existing OSF amendment
(bodies are byte-locked to OSF).

### STEP G — THE END-TO-END READ-PATH PROOF ON REAL DATA

After the `.rds` land, run one AFR `run_finemap` for a curated region with an M2 counterpart and
confirm from its output JSON that **`ld_file_declared` and `ld_matrix` are the SAME
`AFR_aou/…rds` path**, and that `ld_matrix` is **neither `identity`/`identity_fallback` nor an
`AFR/…` path**. That is `resolved == what-the-script-opens`, observed **on production data rather
than on a fixture** — the production form of the DEC-2026-08-05 acceptance test that `L-13`
verifies only on fixtures.

---

## §6 — OPEN ITEMS AT FIRE TIME

Every row answers **BLOCKS THE FIRE?** explicitly. **Most of these bound USAGE, not firing** —
that distinction is the point of this table.

**⚠ READ THIS ROW FIRST — it is the one open item that changes WHAT THE MONEY BUYS.**

| Item | State | BLOCKS THE FIRE? | What it BOUNDS | Where it lives |
|---|---|---|---|---|
| **BLOCKER-D — converter sizing** | ◐ **PARTIAL** | **NO.** The producer writes `.npz`; the OOM is on the **CONSUMER**. STEP B is unaffected | ⚠ **MATERIALLY BOUNDS THE DELIVERABLE.** Only SH2B3 `__sub14` (**22.8 GB**) is convertible, on a big-memory node. **MC4R (67.3 GB)** and **FTO/HLA (~553 GB)** **FAIL FAST** at `m3_convert_max_n_var=120000` (`L-09`) rather than OOM-killing. A sparse `.npz` is a **producer-side change to a FROZEN file**. **Consequence, stated plainly: the fire banks `.npz` that CANNOT be converted for the large regions, so STEP E and the STEP G read-path proof are demonstrable only on the convertible subset.** | HANDOFF `gates.blocker_d_converter_oom` + `resume_on_reconnect` #3 (2026-08-07) |
| **The three E-2 disclosure obligations** — **ROW REFRESHED 2026-08-12** | **DECIDED as option A** (`DEC-2026-08-07-e2-orientation-disposition`). **Obligation (3) is ✅ DISCHARGED** — `DEC-2026-08-11-e2-framing-correction` chose framing **B, CORRECTION**. **Obligations (1) and (2) remain ⛔ UNDISCHARGED and are CARTER'S EXTERNAL ACTIONS** | **NO** | **BOUNDS publication of any AFR coloc number.** (1) the manuscript paragraph, placed by Carter; (2) the OSF record entry, posted by Carter **and** its URL + timestamp recorded in `.planning/osf_deviations.md`; (3) ✅ settled — framing B. ⚠ **Do NOT quote the pooled 5.29% alone** — it is dragged down by the two clean large regions (`CXADR` 0.06%, `MC4R` 0.07%) and hides that two loci sit near 20%; `SH2B3_12q24` tile 3 is **20.33%** while its md5-pinned **anchor** tiles are **0.00%**. ⚠ **And do not quote a corpus figure without its unit** — 17.82% is the **tile-row** median; the **locus** median is 0.4234% | ⚠ **CURRENT OUTGOING TEXT = the v2 pair** at `.planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-SELECTED-PAIR-correction-v2.md`, gated by `260812-09a-check-v2-pair.sh`. The `260811-oku` drafts and the `260811-tf3` v1 pair are **superseded history — do not place or post them.** Entry in `deferred-items.md` E-2 |
| **SR4-OPEN** — **ROW REFRESHED 2026-08-12** | ✅ **DECIDED, no longer open** — `DEC-2026-08-11-sr4-disposition`: **NEVER-FROZEN for all five** files, which is what the dossier's evidence supported | **NO** | **BOUNDS any claim that a file is "frozen".** The five are never-frozen; the only genuinely gated files are the three named by `tests/m3/test_source_freeze_pins.py` (see §7). Any surface still calling one of the five "frozen" or "byte-unchanged" is stale — the canonical list of such sites is the `DEC-2026-08-12` stale-site table | `.planning/DECISIONS.md` `DEC-2026-08-11-sr4-disposition`; dossier at `.planning/quick/260811-pmv-…/260811-pmv-DOSSIER.md` (2026-08-11) |
| **The OSF Check-2 amendment-update** | **NOT POSTED** | **NO** | **BOUNDS CITATION.** No redefined Check-2 result may be cited as **PASSED** until it is posted and its GUID recorded in-repo. STEP F routes it | HANDOFF `gates.osf_pre_registration`; §5 STEP F |
| **The pre-registered 4-check validation protocol** | **NEVER RUN** — zero artifacts (`L-19`) | **NO** | **BOUNDS dev→production promotion and publication.** AOU-LD-PIPELINE.md §9 calls it *"a hard gate for promoting the pipeline from dev to production"* | `L-19`; HANDOFF `gates.validation_4check` |
| **K-2 — the `ld_allele_join.R` extraction** | **DECLINED**, on the merits | **NO — and it is NOT an open risk against the fire** | ⚠ **State it correctly: the decline PROTECTS the fire path.** It was declined **on fire-path-risk grounds** — it would introduce a **first-of-its-kind runtime `source()` dependency** on the exact code path the ~11-day fire exercises (`run_susie_rss.R` has **zero** `source()` calls today). Freeze economy is not sufficient justification to accept fire-path risk | `deferred-items.md` K-2 |
| **The identity-LD caveat on every E-2 number** | **STANDING** | **NO** | **BOUNDS how E-2's numbers may be cited.** Every panel behind them is an **identity-LD stub** (`use_identity` TRUE, `R` NULL, EUR/AFR/TRANS byte-identical, md5-verified on two regions). The numbers are the **catalog↔panel-frame transposition rate and nothing more** until a real panel exists — **not** the real-LD exposure | HANDOFF `verified_this_session_firsthand[8]`; `deferred-items.md` E-2 evidence update |
| **Findings E and G — INERT BUT CORRECT** | **CLOSED AS WIRING** | **NO** | **BOUNDS what may be claimed closed.** **E** is safe today **only** because **ZERO AFR QTL-coloc jobs exist at all** (E-4: `_ancestry_for_region` returns `"EUR"` unconditionally) — machine-verified wiring, **not** a production-exercised fix. **G** makes TRANS's failure **VISIBLE**; it does **not** make TRANS work (TRANS still resolves to the 1kG EUR panel). Neither may be cited as *"production-exercised"* | HANDOFF `inert_but_correct` (2026-08-07) |
| **Manifest-egress gap (PRE-FIRE 1)** — **ROW REFRESHED 2026-08-12 EVENING** | ✅ **LANDED** (`5284505`, quick-260812-ox1) — no longer open, no longer a decision; branch (i) is the live default | **NO** | The per-drop provenance the OSF amendment-update commits to publishing is now **SECURED on the happy path** (per-region manifest uploaded inside `if ok:`); the residual branch-(ii) state (best-effort append failure / resume-skip) stays diagnosable post-fire and loud at GATE-1 | §5 PRE-FIRE 1 (superseded analysis, preserved); `260812-ox1-READY-TO-FIRE.md` item 7 |

---

## §7 — EVIDENCE INDEX

| Artifact | Path | Date |
|---|---|---|
| This review's raw command log (verbatim, 20 checks + 3 context blocks) | `.planning/quick/260811-rcw-…/260811-rcw-evidence.log` | 2026-08-11 |
| Machine-readable checklist (header + 20 rows) | `.planning/quick/260811-rcw-…/260811-rcw-evidence.tsv` | 2026-08-11 |
| Layered record (a) — the most recent | `.planning/HANDOFF.json` | 2026-08-07 |
| Layered record (b) | `.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-BLAST-RADIUS.md` | 2026-08-05 |
| Layered record (c) — stale on the producer, valid on GATE 0/1/1.5 | `.claude/skills/aou-ld-pipeline/SKILL.md` | predates the arc |
| Source of truth for §5 | `.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md` `:1302-1536` | — |
| Deferred items (E-2 + its evidence update, E-3, E-4, K-2, K-3, SR4-OPEN) | `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` | through 2026-08-07 |
| Decision — the BLOCKER-1 remedy + its acceptance test | `.planning/DECISIONS.md` `DEC-2026-08-05-m3-ld-read-path` (`:1014-1036`) | 2026-08-05 |
| Decision — E-2 disposed as option A | `.planning/DECISIONS.md` `DEC-2026-08-07-e2-orientation-disposition` (`:1173`) | 2026-08-07 |
| Decision — the freeze is a CODE pin, not a byte pin | `.planning/DECISIONS.md` `DEC-2026-08-06-sr4-freeze-scope` | 2026-08-06 |
| Egress-unit redefinition (44 → at most 22) | `.planning/amendments/m3-egress-and-validation-protocol-addendum.md` §(a) | — |
| Sibling arc — E-2 disclosure drafts (both framings); obligations still UNDISCHARGED | `.planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-SUMMARY.md` | 2026-08-11 |
| Sibling arc — SR4-OPEN dossier; disposition deliberately NOT recorded | `.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-SUMMARY.md` | 2026-08-11 |

### ⚠ THE RETRACTED FREEZE CLAIM — stated here so it is not repeated

**The claim "all 7 pinned files 0-line diff vs `bf16289`" is RETRACTED** (HANDOFF
`verified_this_session_firsthand[5]`). `bf16289` appeared in **ZERO** places across `src/`,
`tests/`, `config/` and `Snakefile` — **nothing ever enforced it** — and **5 of the 8** files had
drifted. **It is not repeated as fact anywhere in this review.**

**Every freeze this review asserts names the test that fails when it breaks:**

| Asserted invariant | Named enforcer |
|---|---|
| `run_susie_rss.R` is **CODE**-frozen at `bf04199` (comments deliberately FREE) | `tests/m3/test_source_freeze_pins.py` (`R_CODE_REF` at `:63`), via `tests/m3/source_freeze.py`; ran inside `L-03` |
| `plink_ld_to_npz.py`, `condition_ld_matrix.py`, `occlusion_span_filter.py` are the **only three** genuinely gated files | `tests/m3/test_source_freeze_pins.py` (`:84-86`); ran inside `L-03` |
| The `params.region_id` guard rail is unchanged | measured directly by **`L-12`** (= 1); additionally `tests/m3/test_occlusion_lockstep_wiring.py::test_params_region_id_is_untouched`, which ran inside `L-03`'s 902 but was **not** isolated by name in this review |
| `--ld-file {input.ld_matrix}` is threaded into the rule's `shell:` | measured directly by **`L-11`** (= 1); behaviourally by `L-13`, at production thresholds by `L-14` |

**No other freeze or invariant is asserted in this document.** Any statement about the fire's
perimeter state in §4 is labelled **last-known**, is **UNENFORCED by anything on this side of the
boundary**, and is re-checkable only by Carter's gate-time command.

---

## Reconciliation log (Task 3)

Every numeric and proper-noun claim above was walked top-to-bottom and traced to (a) a `check_id`
in `260811-rcw-evidence.tsv`, (b) a named in-repo record with a date, or (c) an arithmetic
derivation **re-performed here rather than copied**.

⚠ **SCOPE OF THE ENUMERATION, stated so it can be reproduced: §0 through §7 only — i.e. this
file UP TO the `## Reconciliation log (Task 3)` heading.** This section is the *record of* the
enumeration, not a subject of it, and it necessarily adds numbers of its own; counting the whole
file instead gives 961 / 189 / 68 / 83 and would look like a contradiction. Under that scope:
**831 numeric literal occurrences (174 distinct)**, **65 distinct proper-noun claims** (file
paths, test names, decision ids), **80 `L-NN` citations**, and **26 arithmetic claims
re-performed** (the eight E-2
per-region ratios plus four column-sum checks; the 153/123/276 and 276×2=552 region arithmetic;
the 575-job DAG sum; six BLOCKER-D size derivations plus the ceiling comparisons and the
float64/float32 factor; the cost-band and wall-clock divisions; the SH2B3 87.2%/12.8% split; the
corpus pooled 4.18%; the `L-06` output-line count; and the commit-range count).

**Seven defects found and fixed. This pass was not a formality.**

- 2026-08-11 — **FIXED: a wrong number shipped into the reader-facing table.** `L-06`'s observed
  value said the `--list` output was "928 lines" → now **"926 output lines, of which 148 are rule
  names"**. The 928 came from an off-by-one in my own throwaway `awk` (`NR-start-2`); re-measured
  by indexing the log between the `$ ` line and the `--- exit:` line. Corrected in **both** the
  review and `260811-rcw-evidence.tsv`. (source: `L-06`, re-derived)
- 2026-08-11 — **FIXED: the SuSiE quality-gate line number, the one STEP A sends Carter to read.**
  Cited as `run_susie_rss.R:184` (from the m3-04c PLAN; the blast radius says `:216`) → now
  **`:500`**, with the thresholds loaded at `:713-716`. Both older pointers land on unrelated
  lines. Recorded as a new divergence §2.1(8). (source: measured at `c4dc410`)
  — ⚠ **ITSELF CORRECTED 2026-08-12 (B-LOW-1): the threshold range in this 2026-08-11 entry is
  wrong.** The three assignments are at **`:716-718`** (`MIN_LD_OVERLAP` `:716`,
  `MIN_LD_COVERAGE` `:717`, `MIN_LD_MIN_USE` `:718`); `:715` is the `yaml::read_yaml` call. The
  `:713-716` written here excluded two of the three. **The entry is left in place as the record
  of the 2026-08-11 pass; this note supersedes its range.** (source: re-measured at HEAD
  2026-08-12)
- 2026-08-11 — **FIXED: `provenance_source` scalar-assignment line.** `assemble_occlusion_catalog.py:202`
  (m3-04c PLAN) → **`:230`** (`df["provenance_source"] = provenance`). `:202` is a string fragment
  inside an unrelated message. (source: measured at `c4dc410`)
- 2026-08-11 — **FIXED: the GRCh38 varid-format citation**, which is what makes the degraded
  reconstruction recoverable at all. `run_native_ld_panel.py:391-400` (m3-04c PLAN) → **`:507`**.
  `:391-394` is a docstring about `.bim` row order. (source: measured at `c4dc410`)
- 2026-08-11 — **FIXED: the `gs://` upload-set citation**, the proof the manifest is not uploaded.
  `:922-938` → **`:922` (`if ok:`) with the three uploads at `:925-926` (`.npz`), `:929`
  (`.afreq`), `:935-937` (`.occluded.excludelist`)**. (source: measured at `c4dc410`)
- 2026-08-11 — **FIXED: the manifest-write attribution.** "`run_native_ld_panel.py:822` writes
  `{compute_dir}/occlusion_manifest.tsv`" → **`:822` CALLS `ocm.append_occlusion_rows(...)`
  (inside the best-effort `try:` at `:821`); the write itself is `occlusion_manifest.py:203-208`**.
  (source: measured at `c4dc410`)
  — ⚠ **ITSELF CORRECTED 2026-08-12 (B-LOW-1): the write anchor in this 2026-08-11 entry is
  wrong.** `:203-208` is `append_occlusion_rows`'s keyword default (`:203`) plus its docstring
  (`:204-212`). The WRITE is in `append_region_manifest`: **`:195-196`** on the append path
  (`with manifest_path.open("a")` → `fresh.to_csv(fh, …, header=False)`) and **`:181`** on the
  fresh-file path. **The entry is left in place as the record of the 2026-08-11 pass; this note
  supersedes its anchor.** (source: re-measured at HEAD 2026-08-12)
- 2026-08-11 — **FIXED: an off-by-one in a citation I introduced.** The identity-LD-stub caveat was
  cited as HANDOFF `verified_this_session_firsthand[7]` → **`[8]`**; `[7]` is the 100×-error entry.
  Verified by parsing the JSON array rather than by eye. (source: `.planning/HANDOFF.json`)

**Checked and found CORRECT (no change needed):** all eight E-2 percentages and their two column
sums (`66,480` exact / `3,714` flipped both reconcile, and the 20.33%-vs-0.20% ratio-versus-percent
trap is re-derived explicitly); `153 + 123 = 276`; `276 × 2 = 552`; `276+276+1+22 = 575`; the
BLOCKER-D float64↔float32 factor of exactly 2 and the `120000` ceiling admitting SH2B3 (75,497)
while excluding MC4R (n ≈ 129,711) and FTO/HLA (363k–372k); `263 h ÷ 24 ≈ 11 days` and
`312 h = 13 days`; `523,169 ÷ 600,000 = 87.2%`; the corpus pooled `31,152 / 745,534 = 4.18%`;
the panel TSV's **9** columns with `n_dropped_occluded` at index **7** (re-parsed with `ast` after
a naive comma-split gave a wrong 12 — log block `CONTEXT-C`); the 15-commit docs-only range
touching **0** files under `src/`/`tests/`/`config/`/`Snakefile` (`CONTEXT-A`, `CONTEXT-B`); and
`HANDOFF do_not[0]` as the never-fire rule.

**Guard rails, re-checked after the fixes:** the verdict is mechanically consistent with the
evidence (20/20 `PASS` ⇒ the GREEN form; exactly **1** verdict line, **0** NOT-READY lines);
every `L-NN` cited resolves to a real TSV row (20 of 20, no unknown ids); every asserted freeze
names its enforcing test or is written as unenforced; `bf16289` appears **twice and only as the
retraction**; no divergence is presented as a merged status without its seam; and
`grep -cE '^\$ .*(gsutil|gcloud|bq |wb )' 260811-rcw-evidence.log` = **0**.

---

## Corrections (2026-08-12)

**What this section is, and what it is NOT.** It is a **corrections layer over a dated
measurement**, not a re-measurement. **The 2026-08-11 anchor (`c4dc410`), the L-01..L-20 evidence
rows, `260811-rcw-evidence.log` and `260811-rcw-evidence.tsv` are UNCHANGED** and were not re-run.
Every correction below is a defect in this document's own text or a status that moved after
2026-08-11; each was **re-anchored against the tree at HEAD on 2026-08-12** before being written
down, per this document's own §2.1(8) discipline — and where a re-anchoring disagreed with the
finding that ordered it, **the measured value won and the disagreement is recorded here.**

Source: the 2026-08-11/12 five-way adversarial review of `7d575a5..42c060e` (Codex CLI v0.141.0
+ four blind read-only investigators). Remediation task: `quick-260812-09a`. Acceptance harness:
`.planning/quick/260812-09a-…/260812-09a-check-review.sh`.

⛔ **Still true of this document after the corrections:** zero perimeter contact was made in
producing them (**no `gsutil`, `gcloud`, `bq` or `wb` was invoked** — every command in §4 and §5
remains an instruction **for Carter**), nothing was fired, and no file outside this review and
the `260812-09a` quick directory was touched by this pass.

| # | Finding | What changed | Where | Evidence |
|---|---|---|---|---|
| 1 | **B-BLOCKER-1** | The liveness-poll command `gsutil ls gs://${WORKSPACE_BUCKET}/…` **double-prefixed** and would have FALSE-PASSED the pre-fire "expected 0" row and read a healthy fire as dead. Replaced at **all three points of use** with a **literal-bucket primary form**, a correctly-quoted env alternate, and an explicit **never-prefix** warning at each site | §4 row 1 (bucket `.npz` count); the **⚠ THE LIVENESS ARBITER** block (command added — it previously had none); **§5 STEP B** (command added — it previously had none) | `SKILL.md:43` (the variable must print `gs://rw-migration-aou-rw-476cdac2`, i.e. it already carries the scheme); producer path re-verified at HEAD: `run_native_ld_panel.py:925-926` uploads `{gs_out_dir}/{region_id}.npz`, `gs_out_dir = str(out_dir)` at `:732`. Same defect class as **quick-260611-tbw** (`fix-aou-2-workspace-bucket-double-prefix`, gap C3) |
| 2 | **B-HIGH-1** | Added the m3-04c PLAN's **"276 is NOT a pass bar"** caveat — a partial bank is a real, reportable outcome — to the liveness-arbiter block **and** to STEP B, plus a pointer from §4 row 1. Also softened "climbing **to** 276" to "climbing **toward** 276" at both sites | liveness-arbiter block; §5 STEP B; §4 row 1 | m3-04c PLAN `:1503-1504` (verbatim caveat). ⚠ **Re-anchored, and the finding's pointers moved:** the review order cited PLAN `:1494-1497` (measured: `:1503-1504`), producer `:920-926` for the never-upload path (measured: `:917` stamps `verify_failed`, `:922`'s `if ok:` gates the upload, `:939-940` leaves it in scratch) and `:942` for the continue-on-error (measured: the `except Exception` is `:943-945`; `:942` is an unrelated assignment). **The measured values are the ones written down.** |
| 3 | **B-MEDIUM-1** | §6 open-items table: the **E-2 row** now records obligation **(3) DISCHARGED** (`DEC-2026-08-11-e2-framing-correction`, framing B) with **(1) and (2) still open as Carter's external actions**, and points at the **v2 pair** as the current outgoing text; the **SR4-OPEN row** is now **DECIDED** (`DEC-2026-08-11-sr4-disposition`, never-frozen). Both rows carry the refresh date | §6 rows 2 and 3 | `.planning/DECISIONS.md` `DEC-2026-08-11-e2-framing-correction`, `DEC-2026-08-11-sr4-disposition` |
| 4 | **B-MEDIUM-2** | `<panel-uri>` placeholder replaced with the **actual URI**, `gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv`, with the derivation recorded inline | §4 row 3 | **Derived from the producer at HEAD, not taken from the reviewer's guess:** `run_native_ld_panel.py:122` `_DEFAULT_PANEL_NAME = "m3-W2-native-plink-panel.tsv"`; `:734` `panel_tsv = panel_tsv or _gs_join(gs_out_dir, _DEFAULT_PANEL_NAME)`; `:732` `gs_out_dir = str(out_dir)`; module docstring `:69,:72` gives `--out-dir gs://<bucket>/ld/AFR_aou`; bucket from `SKILL.md:12,:43`. The independently-derived string **agrees** with Codex's — agreement, not confirmation-by-repetition |
| 5 | **B-MEDIUM-3** | The real-`.bim` row's un-runnable "Byte-check…" instruction replaced with an **honest statement**: the exact command is determined in-perimeter (the real cohort `.bim` path is fixed at cluster build time and is not recorded on this side), and the **0-vs-1-based index-origin question is OPEN** and must be settled first | §4 row 4 | m3-07 / m3-16 record; the expected id set is unchanged |
| 6 | **B-MEDIUM-4** | The egress-ruling, CDR-pin and cohort-rebuild rows now carry **"LAST-KNOWN (dated record; not re-verifiable from NC State)"** labels, each with an explicit ruling on whether fire-time re-verification is required. **A new §4 row 5 was ADDED** for the cohort MTs, because they are mutable state the fire reads | §2 rows for GATE 0 / GATE 1 / GATE 1.5; new §4 row 5 | Skill **invariant 1** (`SKILL.md:19`): `_SUCCESS` is not evidence of data — verify `gsutil du -s …/entries/rows/parts/` **and** `count_cols`/`count_rows`. Canonical MT path carries **no `/mt/` subdirectory** |
| 7 | **B-MEDIUM-5** | New **§2.1(9)**: the m3-04c PLAN contradicts itself on which branch admits `provenance_source == excludelist_degraded` (`:1395` says branch (iii); `:1508` says branch (ii)). The **code-correct reading** is stated so a post-fire auditor is not hit cold at STEP E | §2.1, new item (9) | Re-measured at HEAD: `assemble_occlusion_catalog.py:230` scalar provenance; **GATE 1** `:415` (`if orphaned and not allow_partial_manifest:`) raising at `:416` = branch (ii), flag `allow_partial_manifest`, stamp stays `stage_a_manifest`; **GATE 2** `:456` chooses `PROVENANCE_EXCLUDELIST_DEGRADED`, `:460` (`if not allow_degraded:`) raises at `:462` = branch (iii). ⚠ The finding cited the GATE-1 raise as `:415`; measured, `:415` is the condition and `:416` is the `raise` — both are recorded |
| 8 | **B-LOW-1** | Three wrong line corrections fixed **and their echoes chased**: (a) the `occlusion_manifest.tsv` write is `append_region_manifest` `:195-196` (fresh-file `:181`), **not** `:203-208` — which is a keyword default plus a docstring; (b) `run_native_ld_panel.py:507` is **inside a docstring** (`:498-511`) and there is **no code line** in that file asserting the varid format, so it is now cited as documentation rather than as an enforced invariant; (c) the `MIN_LD_*` thresholds are `:716-718` (policy read at `:715`), **not** `:713-716`, which excluded two of the three | §2.1(8) table (two new rows + one row amended); §5 PRE-FIRE 1 paragraph; §5 STEP A paragraph | Measured at HEAD 2026-08-12. ⚠ The finding gave the threshold range as `:715-718`; measured, `:715` is the `yaml::read_yaml` call and the three assignments are `:716-718`. **Both are stated** rather than one silently adopted |
| 9 | **B-LOW-2** | *"four `test_negative_control_pre_change_*` tests"* → **three** (`:935`, `:1018`, `:1296`) | §3, the BLOCKER-1 two-suites bullet | `grep -c 'def test_negative_control_pre_change' tests/m3/test_ld_declared_authoritative.py` = **3** |
| 10 | **B-LOW-3** | `L-11`'s and `L-09`'s labels rescoped to claim exactly what their commands prove. **L-11** is a **file-wide grep**, not a rule-scoped one — the scoped proof is `L-13`'s `test_run_finemap_shell_passes_the_declared_ld_matrix`. **L-09** reads a **config value only** — the fail-fast enforcement is not measured by the L-set | §3 table, rows `L-09` and `L-11` | `tests/m3/test_ld_read_path.py:251`; enforcement chain `src/snakemake/rules/m3_convert_npz_rds.smk:132` → `:163` → `:180` and `src/scripts/ld_npz_to_rds.R:272`. ⚠ Note the R script lives at **`src/scripts/`**, not `src/snakemake/scripts/` |
| 11 | **B-LOW-4** | `L-16` annotated for its **`2>/dev/null` missing-directory blindness**: an absent directory and an empty one both print `0`. Harmless for the pre-fire expectation, **not harmless post-fire** | §3 table, row `L-16` | The command as run, from `260811-rcw-evidence.log` `##### L-16`: `ls data/interim/aou_ld_exports/AFR_aou/*.npz 2>/dev/null \| wc -l` |

| 12 | **EVENING (blast-radius sweep)** — status change, not a text defect: **PRE-FIRE 1 LANDED** as this review's own §5 "LOWER-RISK OPTION, PREFERRED" (per-region `{region_id}.occlusion_manifest.tsv` uploaded inside `if ok:`), so the §2 gate row, the §5 recommendation and the §6 open-item row are refreshed in place with the date; **1b branch (i) is the live default** and the operative surface is the `260812-ox1` READY-TO-FIRE runbook item 7 | §2 gate table row; §5 PRE-FIRE 1 (banner); §6 row 9 | `5284505` (quick-260812-ox1; TDD, verifier 9/9); `260812-ox1-READY-TO-FIRE.md` |
| 13 | **EVENING (blast-radius sweep)** — status change: **the PRE-FIRE 3 index-origin question is SETTLED CODE-SIDE.** The gated test `tests/m3/test_occlusion_span_filter.py:492` computes both sides in the same 0-based `enumerate` space (`:520` vs the `:186` constant), so an origin error fails LOUDLY — it cannot false-pass; the §4-row-4 "settle it first" manual-comparison instruction is superseded and the manual comparison is FORBIDDEN (the off-by-one false-pass risk belonged to it alone). The source doc's base is unrecoverable (its adjacency language is base-invariant), so the gated test IS the instrument | §4 row 4; §5 PRE-FIRE 3 | quick-260812-ox1 evidence (CONTEXT-P3 blocks); `260812-ox1-READY-TO-FIRE.md` item 8 |

**Nothing in §1's verdict changed.** The verdict covered agent-verifiable preconditions at
`c4dc410`; none of the corrections above touches an `L-NN` result. *(Entries 12-13, added
2026-08-12 EVENING, are STATUS refreshes — two items this review correctly called open were
subsequently closed by quick-260812-ox1; the analysis bodies are preserved and the refresh
is dated at every touched row.)* What changed is that two of
the fire-time instructions this document hands Carter were **wrong in a direction that reads as
success** — a poll that returns 0 on a usage error, and a count treated as a pass bar — and both
now say what they mean at the point the reader meets them.
