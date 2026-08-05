---
phase: m3-aou-afr-ld-panel-build
plan: 04c
type: execute
wave: 2
depends_on: ["04b"]
files_modified:
  - src/python/build_curated_m2_crosswalk.py
  - config/curated_to_m2_region_map.tsv
  - src/snakemake/rules/finemap.smk
  - src/legacy/region_analysis/scripts/run_susie_rss.R
  - src/python/plan_ld_egress.py
  - src/snakemake/rules/m3_ingest_aou_ld.smk
  - src/snakemake/rules/m3_convert_npz_rds.smk
  - .planning/amendments/m3-egress-and-validation-protocol-addendum.md
  - .planning/amendments/aou-egress-audit-log.md
  - .planning/ROADMAP.md
  - tests/m3/test_curated_m2_crosswalk.py
  - tests/m3/test_ld_read_path.py
  - tests/m3/test_occlusion_lockstep_wiring.py
  - tests/m3/test_ld_panel_resolver.py
  - tests/m3/test_m3_ingest_convert_destale.py
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "The AFR_aou panel is REACHABLE from run_finemap, which requires BOTH fixes and is FALSE with either one alone. (a) THE CROSSWALK: REGION_SAFE_TO_ID is built only from config/regions_curated.csv (12 curated Track-A slugs, region_id == the slug), while the AFR_aou chain head templates on {region_id} = m2_region_NNNNN; config/region_id_mapping.tsv holds ZERO curated slugs, so resolve_ld_path asks for a filename the producer never writes. (b) THE READ PATH: {input.ld_matrix} is a DAG DECLARATION ONLY -- it appears nowhere in run_finemap's shell:, and run_susie_rss.R rebuilds its own path as file.path(ld_dir, ancestry, region_id.rds) with ancestry='AFR', never 'AFR_aou', falling to an identity matrix on a miss. Fixing (a) alone changes WHICH nonexistent path Snakemake demands; fixing (b) alone hands the script a path the crosswalk never corrected. Both, or the ~11-day fire buys nothing."
    - "resolved == what-the-script-opens is PROVEN, not asserted. run_finemap's shell: passes --ld-file {input.ld_matrix}, and load_ld_matrix opens that exact file in preference to any ld_dir reconstruction -- verified behaviourally by running the REAL R loader against an AFR_aou-shaped .rds that is absent from the ld_dir candidate set. A green DAG is NOT evidence (DEC-2026-08-05-m3-ld-read-path)."
    - "The --ld-dir reconstruction survives as a FALLBACK, so every caller that does not pass --ld-file behaves character-for-character as today, including the both-absent case which still returns status='ld_dir_missing'."
    - "The crosswalk changes ONLY the region_id argument passed to resolve_ld_path (finemap.smk:174). run_finemap.params.region_id (finemap.smk:206) keeps resolving through REGION_SAFE_TO_ID, because it feeds run_susie_rss.R --region, which looks the id up in config/regions_curated.csv."
    - "A curated region with no M2 counterpart (BMI_Xq24 is chrX; M2 is autosomes-only per D-M2-09) is recorded as status=unmapped and falls through to the legacy chain, so the resolved path string is byte-identical to today's."
    - "The crosswalk compares PHYSICAL intervals, not the parent-repeated grch37 columns. All 18 subregions of m2_region_00040 carry an IDENTICAL start_grch37/end_grch37 (the parent's ~89 Mb bounding box copied verbatim); only the *_grch38 columns vary per subregion. A smallest-containing-span rule over those columns is a perfect 18-way tie that lexicographically returns __sub00, whose real GRCh37 window (37,857,542-45,792,298) has ZERO bp overlap with SH2B3 and sits ~66 Mb away. Candidate windows are therefore lifted GRCh38->GRCh37 (the repo ships ONLY hg38ToHg19.over.chain.gz) before any containment test."
    - "The crosswalk oracle is validated by PHYSICAL OVERLAP, not by re-running the selection. A test that re-implements the same comparison cannot catch this class of bug -- which is exactly how a prior 12/12 'independent reproduction' reproduced the defect instead of finding it. The suite asserts positively that the selected window overlaps the curated interval, and pins __sub00 as NOT selected for SH2B3."
    - "The two tests that hard-fail on the exact edits this plan must make are REWRITTEN STRICTLY STRONGER, in named steps, with before/after text spelled out -- never left to executor improvisation, and never by weakening the params.region_id guard rail that sits immediately above one of them. Neither rewrite may leave an assertion that cannot fail: the resolve_ld_path kwarg test is re-anchored to a BALANCED-PAREN extraction of the real call site (the module docstring mentions resolve_ld_path() twice, so a non-greedy regex silently matches from the docstring and can never fail), and the plan carries an executable NEGATIVE CONTROL proving it still fails when a kwarg is removed."
    - "run_susie_rss.R's Path-2 revert (ld_overlap == 0, NOT ancestry-gated) becomes OBSERVABLE: it sets variant_catalog_fallback like Path 1 does, sets a NEW ld_overlap_zero_fallback flag that distinguishes the two, and both are READ by the per-region estimate_s log so the flags stop being write-only. Science behaviour is unchanged."
    - "m3_ingest_aou_ld.smk and m3_convert_npz_rds.smk match the REAL producer: AFR-only (EUR is the public UKBB 337k panel, EUR_aou will never be populated), 276 regions not 322 cells, and a region_id wildcard that admits the 123 subregion-split ids (m2_region_00040__sub00) the current r'm2_region_\\d{5}' silently excludes."
    - "The egress plan is produced by the EXISTING ld_egress_bundle.plan_egress_bundles. src/python/validate_bundle_sizes.py is NOT written: its function already shipped at ade6066."
    - "The egress UNIT is redefined and RECORDED: the producer writes per-region .npz DIRECTLY to gs://<bucket>/ld/AFR_aou/{region_id}.npz, so no stage exists at which a per-chromosome bundle OBJECT exists. Bundles are REQUEST-LEVEL groupings of object URIs, at most 22 AFR chromosome groups plus size splits, not 44."
    - "REQ-AOU-LD-VALIDATION Check 2 (AOU-LD-PIPELINE.md 9.2, 'AoU EUR vs 1000G EUR entry-wise r >= 0.97') is STRUCTURALLY UNRUNNABLE because there will be no AoU EUR panel. It is REDEFINED in writing, not silently dropped, and the redefinition is flagged for an OSF amendment-update because 9 is a pre-registered hard gate."
    - "The 50 GB egress ceiling is recorded as a CONSERVATIVE PROJECT WORKING CEILING, not a documented hard AoU API limit (ld_egress_bundle.py:9-15). The stale m3-04 plan treated it as hard fact."
    - "The allow_degraded DEAD-END is closed IN THE GATE: config/pipeline.yaml:266 sets allow_degraded=false and assemble_occlusion_catalog.py RAISES when excludelists exist but manifests do not -- exactly the post-fire state if PRE-FIRE 1 is declined. The fail-loud design is correct; the gate records the decision rather than discovering it after ~$385-1,084."
    - "ROADMAP line 211 is replaced and m3-05 is marked SUPERSEDED-PENDING-REPLAN, because m3-05 inherits the same stale basis (322-row SHA-256 monolith, 44 sub-manifests, EUR_aou .rds, Path A.1/A.2/A.3 region counts)."
    - "Frozen contracts (plink_ld_to_npz.py, ld_npz_to_rds.R, condition_ld_matrix.py) and the four m3-07 modules keep a 0-line git diff against the plan's start commit. m3-06 stays HELD: no NaN->0 revival, no condition_ld_matrix import."
  artifacts:
    - path: "src/python/build_curated_m2_crosswalk.py"
      provides: "Deterministic curated-region to M2-region crosswalk builder. Lifts each candidate M2 window GRCh38->GRCh37 (hg38ToHg19 chain) so the comparison happens in ONE build, tests containment against the curated GRCh37 interval, and ranks containing candidates by CORE overlap first. Explicit partial/unmapped status."
      min_lines: 90
    - path: "config/curated_to_m2_region_map.tsv"
      provides: "12-row crosswalk: region_safe, curated_region_id, m2_region_id, chr, curated/M2 GRCh37 spans, containment, status"
    - path: "src/legacy/region_analysis/scripts/run_susie_rss.R"
      provides: "The --ld-file thread: an explicit LD artifact path that takes precedence over ld_dir reconstruction, with the ld_dir-absent guard handled, plus Path-2 revert observability"
      contains: "ld-file"
    - path: "tests/m3/test_ld_read_path.py"
      provides: "The DEC-2026-08-05 acceptance test: static proof the shell passes {input.ld_matrix}, plus BEHAVIOURAL proof the real R loader opens that exact file"
      min_lines: 120
    - path: "src/python/plan_ld_egress.py"
      provides: "Thin CLI over the EXISTING ld_egress_bundle.plan_egress_bundles; consumes a gsutil ls -l capture, emits the per-chromosome AFR egress request plan"
      min_lines: 60
    - path: "src/snakemake/rules/m3_ingest_aou_ld.smk"
      provides: "AFR-only ingest gate, widened region_id wildcard, 276-region manifest expectation, native-plink producer documented"
    - path: "src/snakemake/rules/m3_convert_npz_rds.smk"
      provides: "AFR-only .npz to .rds conversion; build_ld_rds_aou_eur retired with a documented reason"
    - path: ".planning/amendments/m3-egress-and-validation-protocol-addendum.md"
      provides: "The recorded egress-unit redefinition, the Check-2 redefinition (2a/2b/2c), and the EGRESS_CAP_GB provenance correction"
      min_lines: 90
    - path: ".planning/amendments/aou-egress-audit-log.md"
      provides: "APPENDED scope-correction section (44 bundles to at most 22 AFR groups). The file is append-only; the 2026-04-28 ruling text is never rewritten."
  key_links:
    - from: "src/snakemake/rules/finemap.smk"
      to: "src/legacy/region_analysis/scripts/run_susie_rss.R"
      via: "--ld-file {input.ld_matrix} in the run_finemap shell block"
      pattern: "--ld-file \\{input\\.ld_matrix\\}"
    - from: "src/legacy/region_analysis/scripts/run_susie_rss.R"
      to: "data/processed/ld_reference/AFR_aou/{region_id}.rds"
      via: "load_ld_matrix ld_file argument, ahead of the ld_dir candidates"
      pattern: "ld_file"
    - from: "src/snakemake/rules/finemap.smk"
      to: "config/curated_to_m2_region_map.tsv"
      via: "resolve_ld_path(region_id=...) argument"
      pattern: "CURATED_TO_M2"
    - from: "src/snakemake/rules/m3_convert_npz_rds.smk"
      to: "data/processed/ld_reference/AFR_aou/{region_id}.rds"
      via: "build_ld_rds_aou_afr with a widened region_id wildcard"
      pattern: "__sub"
    - from: "src/python/plan_ld_egress.py"
      to: "src/python/ld_egress_bundle.py::plan_egress_bundles"
      via: "direct import; no reimplementation"
      pattern: "plan_egress_bundles"
---

## What changed in this replan and why

Re-anchored at `676fe77` (`finemap.smk` and `run_susie_rss.R` are byte-identical at
`2bda675..676fe77`; `tests/m3/test_occlusion_lockstep_wiring.py` is NOT — it moved in
`quick-260804-rtc`, so its line numbers below are HEAD's, not the blast radius's).

The previous version of this plan was **factually sound and premised wrong**. Its
crosswalk oracle was independently reproduced 12/12 exactly, including the load-bearing
`SH2B3_12q24 -> m2_region_00040__sub00` tie-break — all of that is PRESERVED verbatim.
What changed:

| # | Change | Why |
|---|---|---|
| 1 | **Task 1 now lands TWO fixes, not one: the crosswalk AND the `--ld-file` read-path thread.** | BLOCKER-1. `{input.ld_matrix}` never reaches the shell; the R script rebuilds its own path under `AFR/`, not `AFR_aou/`, and falls silently to identity. The crosswalk alone changes *which nonexistent path Snakemake demands* — it cannot make the artifact readable. Remedy locked by Carter as `DEC-2026-08-05-m3-ld-read-path`. |
| 2 | **`must_haves.truths[0]` rewritten.** | It previously claimed the crosswalk alone delivers reachability. That was **false as specified**. It now names both halves and states that either alone is insufficient. |
| 3 | **Every `finemap.smk` line number re-anchored.** | BLOCKER-3. m3-04b added +48 lines above `params:`. The old plan's `:158` "do-not-touch" guard now points **inside the `input.ld_matrix` block the executor must edit**, and its "CR-001 comment at `:117-123`" is now m3-04b's own comment (real CR-001 is `:165-171`). |
| 4 | **The BLOCKER-2 test rewrite is its own numbered step with exact before/after text.** | The assertion that must SURVIVE (`test_occlusion_lockstep_wiring.py:435`) sits immediately above the two that must CHANGE (`:439`, `:443`). "Make tests/m3 pass" baits an executor at the one line the project has ruled must never move. |
| 5 | **NEW — a SECOND self-contradicting test found and proved this session: `tests/m3/test_ld_panel_resolver.py::test_finemap_smk_calls_resolver_with_both_kwargs`.** | Its `region_safe` regex is `resolve_ld_path\s*\([^)]*region_safe\s*=`. `[^)]*` cannot cross the `)` that `CURATED_TO_M2.get(...)` introduces. **Proved by simulation: `region_safe kwarg regex=True` at HEAD, `False` post-crosswalk.** The blast radius did not catch this. The test's OWN comment pre-authorizes the fix ("if that ever changes, broaden to a non-greedy `[\s\S]*?`"). |
| 6 | **`snakemake --dry-run --quiet` STRUCK from both tasks; replaced with `snakemake --list`.** | MEDIUM-7 / D-04b-03. `data/processed/ld_reference/` does not exist, so `resolve_ld_path` **raises** — re-verified firsthand for BOTH ids: `FTO_16q12 -> RAISES FileNotFoundError`, `m2_region_00067 -> RAISES FileNotFoundError`. Task 1 does NOT discharge it. Leaving it in invites an executor to touch fake `.rds` files. `--list` exits 0 today and proves the same thing the dry-run was really being used for (every rule file parses and imports). |
| 7 | **HIGH-1 folded into the Task 3 gate as an explicit recorded decision.** | Declining PRE-FIRE 1 dead-ends STEP E *after* the money is spent: `allow_degraded: false` + `assemble_occlusion_catalog.py` raising on excludelists-without-manifests. The old gate's acceptance criteria admitted `excludelist_degraded` as valid without anything flipping the flag. |
| 8 | **HIGH-2 folded into Task 1** (same file, same pass). | Path 2 (`run_susie_rss.R:423-428`) is not ancestry-gated, never sets `variant_catalog_fallback`, and no consumer reads either flag. This plan introduces a NEW LD source with different varid provenance, which **raises** the probability of `ld_overlap == 0`. |
| 9 | **MEDIUM-6 added to the region-1 gate checklist.** | `SH2B3_12q24` maps to a deliberately narrower subregion; `run_susie_rss.R:184` can reject it on coverage and fall to identity with only a `message()`. |
| 10 | **`files_modified` corrected** to include `run_susie_rss.R`, `test_ld_read_path.py`, `test_occlusion_lockstep_wiring.py`, `test_ld_panel_resolver.py`. | The old list omitted files this plan now edits. |

**Revision 2 (2026-08-05, post plan-check). Two CONFIRMED blockers in the version above:**

| # | Change | Why |
|---|---|---|
| 11 | **The crosswalk mechanism is REPLACED, and the oracle RE-DERIVED. `SH2B3_12q24` moves `__sub00` -> `__sub14`.** | ⚠ BLOCKER. All 18 subregions of `m2_region_00040` share an IDENTICAL `start_grch37`/`end_grch37` — the parent's ~89 Mb bounding box copied verbatim (`build_ld_region_manifest.py:585-587,650-653`). "Smallest containing span" was a perfect 18-way tie; lexicographic tie-break returned `__sub00`, whose real GRCh37 window is **37,857,542–45,792,298 — ZERO bp overlap with SH2B3, ~66 Mb away**. The plan would have pointed the Track A ANCHOR LOCUS at an unrelated window's LD panel. The prior "12/12 independent reproduction" re-implemented the same mechanism and reproduced the bug. **1 of 12 mappings moved; the other 11 are re-confirmed by physical overlap.** |
| 12 | **The oracle tests are rewritten to validate by PHYSICAL OVERLAP, plus a regression pin that `__sub00` is NOT selected.** | A test that re-runs the selection cannot catch a wrong selection rule. This is the generalizable lesson from item 11. |
| 13 | **STEP 7's regex fix is REPLACED with a balanced-paren call-site extractor + a mandatory NEGATIVE CONTROL.** | ⚠ BLOCKER. `finemap.smk:9,12` mention `resolve_ld_path()` in the module docstring, so a non-greedy `[\s\S]*?` starts matching there and runs to the next `region_id\s*=` anywhere in the file — including `params.region_id` at `:206`. **Proved: with both kwargs stripped from the real call site, the broadened `region_id` assertion still returns `True`.** The proposed fix would have silently made the assertion vacuous. |
| 14 | **Task 1 SPLIT into 1a / 1b / 1c** (cap lifted by the coordinator), and PRE-FIRE 1b re-anchored + widened to THREE states. | Task 1 was oversized at 8 files and grew again with item 11. The split isolates the historically dangerous test-rewrite step. Separately: `assemble_occlusion_catalog.py:368-380` is docstring prose — the `allow_degraded` raise is at `:460-473`, and `fac9a93` added a SECOND refusal gate (`allow_partial_manifest`, `:415-431`) that can block STEP E in a state PRE-FIRE 1b did not model. |

**Not re-planned here (already CLOSED by `quick-260804-rtc`: `3bb8783` / `bf963df` / `fac9a93`):**
BLOCKER-4, HIGH-0, HIGH-4, D-04b-01, LOW-1. Do not re-plan them.
Suite baseline at `676fe77`: **`tests/m3` = 527 collected, 496 passed / 31 skipped / 0 failed.**

<objective>
m3-04b closed the lockstep seam. This plan closes the remaining gaps between "the panel
exists in a bucket" and "the panel is actually read", and then hands the billable fire to
Carter.

**Gap 1 — the panel is UNREACHABLE, on TWO independent layers.**

*Layer A (which path is requested).* `finemap.smk` translates a region via
`REGION_SAFE_TO_ID`, which `Snakefile:45-62` builds ONLY from `config/regions_curated.csv`
(12 curated Track-A slugs, whose `region_id` column is the slug itself), so it is
essentially the identity map for curated slugs and can never yield `m2_region_00067`. The
`AFR_aou` chain head templates on `{region_id}`. `config/region_id_mapping.tsv` maps M2
synthetic slugs and contains **zero** curated slugs. So `resolve_ld_path` asks for
`AFR_aou/FTO_16q12.rds` — a file the producer will never write.

*Layer B (which path is opened).* `{input.ld_matrix}` **never appears in `run_finemap`'s
`shell:` block** (`finemap.smk:218-237` passes `--sumstats --trait --ancestry --method
--region --regions-csv --ld-dir --variant-list --credible-set --policy --output`, and
nothing else). Repo-wide, the only `shell:` consuming that variable is `qtl_coloc.smk:316`,
a different rule. `run_susie_rss.R:124-127` rebuilds its own candidate list as
`file.path(ld_dir, ancestry, paste0(region_id, ".rds"))` where `ancestry` is `AFR`, never
`AFR_aou`; no rule anywhere promotes `AFR_aou/*.rds` into `AFR/`. On a miss the script
falls to an identity matrix (`:472-476`) — with a `message()`, so "silent" means
non-fatal, not literally quiet.

**Neither fix works alone.** Layer A alone changes which nonexistent path Snakemake
demands. Layer B alone hands the script a path the crosswalk never corrected.
Both, or the ~11-day / ~$385-1,084 fire produces a panel nothing reads.

**Gap 2 — the ingest/convert rules describe a retired producer.** They gate on
per-chromosome flags for `AFR|EUR`, expect 322 cells, and carry a `build_ld_rds_aou_eur`
rule reading a directory that will never be populated (the EUR chain head has been
`EUR_ukbb_pub` since m3-02e). Their `region_id=r"m2_region_\d{5}"` wildcard silently
excludes **123 of the 276** subregion-split ids.

**Gap 3 — two pre-registered protocol items are unrunnable as written**, and must be
redefined in the open rather than dropped: the egress UNIT (there is no bundle object to
size) and REQ-AOU-LD-VALIDATION Check 2 (there will be no AoU EUR panel).

Tasks 1a, 1b, 1c and 2 are NC-State, `$0`, no perimeter. Task 3 is the terminal blocking gate.

Purpose: without Tasks 1a-1c the fire produces a panel nothing consumes. Without Task 3's
PRE-FIRE items the fire produces a panel whose pre-registered provenance never leaves the
perimeter — and, if PRE-FIRE 1 is declined without recording the `allow_degraded`
decision, a catalog rule that refuses to run at all.

Output: a curated-to-M2 crosswalk, a `--ld-file` read path proven end-to-end against the
real R loader, two strictly-stronger test rewrites, de-staled ingest and convert rules, an
egress request planner built on the existing helper, two recorded protocol redefinitions,
an updated ROADMAP, and a fully enumerated human-action gate.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md
@.planning/amendments/AOU-LD-PIPELINE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md
@.claude/skills/aou-ld-pipeline/SKILL.md

Read `DEC-2026-08-05-m3-ld-read-path` in `.planning/DECISIONS.md` (at the end of the file)
BEFORE editing anything. It is a LOCKED decision: do not re-litigate, do not substitute the
promote/symlink rule or the per-ancestry `ld_dir` — both were explicitly REJECTED.

Read ONLY lines 1-50 of `.planning/STATE.md` (732 KB file). Read the STALE
`m3-04-W4-production-and-egress-PLAN.md` for history only — it is left in place
deliberately and must NOT be edited or deleted.

<interfaces>
All re-verified firsthand against the live tree at HEAD `676fe77` (2026-08-04).
`finemap.smk` and `run_susie_rss.R` are byte-identical at `2bda675..676fe77`.

--- LAYER A: THE CROSSWALK FACTS ---
    Snakefile:45-62   REGION_SAFE_TO_ID[safe] = orig, read ONLY from
                      config["paths"]["regions_curated"] = config/regions_curated.csv
                      -> 12 rows, region_id column == the slug, so the map is
                      essentially IDENTITY for curated slugs. It can NEVER yield
                      m2_region_00067. This is why the crosswalk is a SEPARATE,
                      ADDITIVE defect from the read path -- the --ld-file thread does
                      NOT replace it.
    config/regions_curated.csv ids: FTO_16q12, MC4R_18q21, SH2B3_12q24, APOL1_22q12,
                      PYHIN1_1q23, CXADR_F2RL1_6p21, BMI_5q13.3, BMI_Xq24, 9p21_CDKN2A,
                      APOE_19q13, HLA_6p21, SLC2A9_urate.   Columns: region_id, ancestry,
                      chr, start, end, lead_snp, gene, trait_list, source, canonical_pairs
                      (start/end are GRCh37 -- config genome_build: GRCh37).
    config/region_id_mapping.tsv: 276 data rows; region_safe values look like
                      r00001_1_10000_13506933. ZERO curated slugs (grep -c FTO_16q12 == 0).
    config/pipeline.yaml:218  AFR chain head =
                      data/processed/ld_reference/AFR_aou/{region_id}.rds
    src/python/ld_panel.py::resolve_ld_path(region_id, ancestry, config, region_safe=None)
                      substitutes {region_id} and {region_safe} INDEPENDENTLY, and RAISES
                      FileNotFoundError when no chain entry exists on disk.

--- RE-ANCHORED finemap.smk LINE NUMBERS (HEAD 676fe77) ---
    :114-130   the m3-02e/m3-04b LD-BUILD BOUNDARY comment.  *** DO NOT REWRITE ***
               It carries the tokens `m3-04b`, `m3-04c`, `occlusion_lockstep`, `consume`
               and the ABSENCE of `SUPERSEDED-PENDING-REPLAN`, ALL of which
               tests/m3/test_finemap_loader_contract.py:152-165 asserts. The OLD plan told
               the executor to rewrite ":117-123" -- that is THIS block. Do not.
    :131       rule run_finemap:
    :132       input:
    :147-155   sumstats= / variants= lockstep lambdas (m3-04b).  DO NOT TOUCH.
    :156-164   the m3-W3-T2 "OLD:" audit comment for ld_matrix.
    :165-171   the REAL CR-001 comment -- the one that asserts REGION_SAFE_TO_ID performs a
               translation it has never performed ("FTO_16q12 -> m2_region_00067").
               *** THIS is the block to replace. ***
    :172-179   ld_matrix=lambda wildcards: str(resolve_ld_path(...))
    :174         region_id=REGION_SAFE_TO_ID[wildcards.region],   <- THE ONE ARG TO CHANGE
    :177         region_safe=wildcards.region,                    <- leave unchanged
    :203       params:
    :206       region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],
               *** DO NOT TOUCH. *** Feeds run_susie_rss.R --region against
               config/regions_curated.csv.
    :218-237   shell:
    :221-232     the Rscript invocation. It passes --sumstats --trait --ancestry --method
                 --region --regions-csv --ld-dir --variant-list --credible-set --policy
                 --output. It does NOT pass {input.ld_matrix}. That is BLOCKER-1.
    :236       the estimate_s log one-liner (a real, existing JSON-key consumer).

--- LAYER B: THE run_susie_rss.R CONTRACT (the file the --ld-file thread modifies) ---
    :73        load_ld_matrix <- function(ld_dir, ancestry, region_id, subset)
    :74-76     *** THE TRAP ***  the FIRST guard:
                 if (is.null(ld_dir) || ld_dir == "" || !file.exists(ld_dir))
                   return(list(R=NULL, source=NULL, status="ld_dir_missing"))
               A naive --ld-file addition STILL BAILS HERE when ld_dir is absent but a
               perfectly good --ld-file was supplied. Must be handled explicitly.
    :123-127   safe_id <- safe_region_id(region_id); candidates <- unique(c(
                 file.path(ld_dir, ancestry, paste0(region_id, ".rds")),
                 file.path(ld_dir, ancestry, paste0(safe_id,   ".rds"))))
               NOTE R semantics: file.path(NULL, "AFR", "x.rds") -> character(0);
               file.path("", "AFR", "x.rds") -> "/AFR/x.rds". Build dir candidates ONLY
               when ld_dir is usable.
    :134-215   the candidate loop: file.exists -> readRDS -> match_indices -> overlap /
               coverage -> best_partial / best_overlap tracking.
    :184       the acceptance gate: overlap >= MIN_LD_OVERLAP && coverage >= MIN_LD_COVERAGE
               (config/susie_policy.yaml: 50 and 0.5). Relevant to MEDIUM-6 / SH2B3.
    :234-247   option_list; --ld-dir is :241.
    :298       variant_catalog_fallback <- FALSE   (where the new flag is initialized)
    :342-355   Path 1 revert: AFR-gated, empty filtered subset. Sets used_variant_catalog
               <- FALSE AND variant_catalog_fallback <- TRUE. Observable.
    :419-431   Path 2 revert (HIGH-2): repeat{} loop; when ld_overlap == 0 &&
               used_variant_catalog && attempt == 1 it reverts to subset_base and sets
               used_variant_catalog <- FALSE but NEVER sets variant_catalog_fallback.
               NOT ancestry-gated. No distinguishing signal at all.
    :421       THE SOLE CALL SITE:
                 ld_result <- load_ld_matrix(opt$`ld-dir`, opt$ancestry, opt$region, subset)
    :472-476   the identity fallback: message(); R <- diag(nrow(subset));
               ld_source <- "identity".
    :368, :400, :537   opt$`ld-dir` ALSO feeds provenance/reporting. Leave those in place.
    :538       ld_matrix = ld_source  -- ALREADY records the path actually OPENED. Adding
               ld_file_declared alongside it makes "resolved == opened" a per-region
               checkable fact in every output JSON.

    DOWNSTREAM SAFETY (verified): summarize_finemap_results.py reads the JSON with
    data.get(...) against a fixed FIELDNAMES list, so ADDITIVE keys are safe.

--- THE TWO TESTS THAT HARD-FAIL ON THIS PLAN'S EDITS ---
    tests/m3/test_occlusion_lockstep_wiring.py::test_params_region_id_is_untouched
      :435  assert "region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region]," in src
            *** MUST SURVIVE VERBATIM -- THE GUARD RAIL ***
      :439  assert "region_id=REGION_SAFE_TO_ID[wildcards.region]," in src
            <- pins the EXACT string this plan must replace. MUST BE REWRITTEN.
      :443  assert src.count("REGION_SAFE_TO_ID") == 3
            <- brittle whole-file count; the comment rewrite moves it. MUST BE RE-DERIVED.
      The test's own docstring already says m3-04c changes the sibling argument. It is
      self-contradicting BY DESIGN and was always going to need this rewrite.

    tests/m3/test_ld_panel_resolver.py::test_finemap_smk_calls_resolver_with_both_kwargs
      NEW FINDING, proved by simulation this session (the blast radius missed it):
        re.search(r"resolve_ld_path\s*\([^)]*region_safe\s*=", text, re.DOTALL)
        HEAD           -> True
        post-crosswalk -> False        because CURATED_TO_M2.get(...) introduces a ")"
                                       that [^)]* cannot cross.
      The test's OWN comment pre-authorizes a fix: "if that ever changes, broaden to a
      non-greedy `[\s\S]*?` with explicit closing-paren anchoring."
      ⚠⚠ BROADENING ALONE IS NOT ENOUGH AND IS ACTIVELY DANGEROUS. finemap.smk:9 and :12
      mention ``resolve_ld_path()`` in the MODULE DOCSTRING, so a non-greedy scan starts at
      line 9, not at the real call site (line 173), and runs to the nearest subsequent
      ``region_id\s*=`` anywhere in the file — including params.region_id at :206.
      PROVED by sabotage simulation (both kwargs stripped from the REAL call site):
          pattern                      HEAD   post-xwalk   SABOTAGED
          [^)]*      region_id         True   True         False      <- current, sound
          [^)]*      region_safe       True   FALSE        False      <- current, the break
          [\s\S]*?  region_id         True   True         TRUE       <- VACUOUS. never fails.
          [\s\S]*?  region_safe       True   True         False
      => the "closing-paren anchoring" half of the comment is the load-bearing half.
      THE FIX THAT WORKS (validated on HEAD, post-crosswalk, and TWO sabotage variants):
      extract the BALANCED-PAREN argument block of the real call site and assert inside it.
      The docstring mentions are ``resolve_ld_path()`` with EMPTY parens, so keeping only
      non-empty blocks isolates the one true call site. Full helper + negative control are
      spelled out in Task 1a STEP 7.

--- THE R-BEHAVIOURAL TEST HARNESS (already exists -- REUSE, do not build) ---
    tests/m3/test_stitch_subregions_to_rds.py provides:
      _require_m3_r_toolchain() -> (rscript, env)   NO-SKIP: ERRORS (never skips) when the
        m3-r-ld marker env is present. /rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript
        EXISTS on this node -- verified -- so the behavioural tests below genuinely RUN.
      _loader_functions_only(tmp_path) -> a temp .R holding ONLY run_susie_rss.R's function
        prefix (cut at "option_list <-"), so load_ld_matrix can be sourced WITHOUT
        triggering top-level arg parsing.
      R_SUBPROCESS_TIMEOUT_S, LOADER_R, _two_window_fixture, _run_stitch.
    tests/m3/test_finemap_loader_contract.py already drives
      resolve_ld_path -> load_ld_matrix -> susie_rss end to end. Copy its shape.

--- THE REGION MANIFEST (config/ld_regions.tsv) ---
    552 data rows = 276 AFR + 276 EUR; 276 UNIQUE region_id (each id once per ancestry)
    123 of the 276 unique ids carry "__sub" (e.g. m2_region_00040__sub00)
    20 columns incl. region_id, chr, start_grch37, end_grch37, ancestry, parent_region_id,
      subregion_index, n_subregions, region_class, liftover_status

--- THE REAL PRODUCER (off-DAG, in-perimeter) ---
    src/python/run_native_ld_panel.py  (native plink1.9, Hail-free, single AoU VM)
    :733       gs:// mode -> compute_dir is LOCAL SCRATCH
    :822       ocm.append_occlusion_rows(compute_dir, ...) -> {compute_dir}/occlusion_manifest.tsv
    :922-938   UPLOAD SET = {region_id}.npz, {region_id}.afreq, {region_id}.occluded.excludelist
               -> the occlusion manifest is NEVER uploaded.  See Task 3 PRE-FIRE 1.
    :946-953   uploads are gated on ok (content_verify_npz passed)
    Output layout: gs://<bucket>/ld/AFR_aou/{region_id}.npz   (per-region, DIRECT)
    Panel TSV:     gs://<bucket>/ld/AFR_aou/m3-W2-native-plink-panel.tsv  (9 cols since m3-07b)

--- REUSE, DO NOT REWRITE ---
    src/python/ld_egress_bundle.py (ade6066, m3-02d):
        EGRESS_CAP_GB = 50    # CONSERVATIVE PROJECT WORKING CEILING, not a hard AoU limit
        plan_egress_bundles(cell_sizes: list[{region_id, chr, bytes}], cap_bytes=...)
            -> [{bundle_id, chr, region_ids, total_bytes, n_cells}]; within-chromosome
            greedy split to chrN_a / chrN_b when over the cap
        bundle_gib(bundle), n_bundles_over_cap(bundles), chromosomes_split(bundles)
    DO NOT create src/python/validate_bundle_sizes.py. Its function already shipped.

--- CURRENT STALE RULES (re-verified at 676fe77; m3-04b did not touch these) ---
    m3_ingest_aou_ld.smk:120  ancestry=r"AFR|EUR"
    m3_ingest_aou_ld.smk:195-204  expand(..., ancestry=["AFR","EUR"], chr=1..22) -> 44 flags
    m3_ingest_aou_ld.smk:321  ancestry=r"AFR|EUR"
    m3_ingest_aou_ld.smk:322  region_id=r"m2_region_\d{5}"      <- misses 123 __sub ids
    m3_ingest_aou_ld.smk:74   comment "M2 region manifest path (322 rows...)"
    m3_ingest_aou_ld.smk:8-9  docstring mentions BlockMatrix bm/ dirs (Path A.3, RETIRED)
    m3_ingest_aou_ld.smk:289  comment "all 322 cells"
    m3_convert_npz_rds.smk:103,145  region_id=r"m2_region_\d{5}"  (both rules)
    m3_convert_npz_rds.smk:122  rule build_ld_rds_aou_eur       <- EUR_aou never populated
    build_ld_rds_aou_eur has NO code or test references outside .planning docs.
    .planning/ROADMAP.md:200 (**Plans**), :211 (m3-04 entry), :212 (m3-05 entry).
    .planning/amendments/aou-egress-audit-log.md:9 declares the file APPEND-ONLY.

--- LIFTOVER FACTS (verified firsthand 2026-08-05) ---
    The repo ships EXACTLY ONE chain: data/external/liftover/hg38ToHg19.over.chain.gz.
    There is NO hg19->hg38 chain. Do not assume one. Therefore the only direction that
    works today is lifting the CANDIDATE M2 WINDOWS (GRCh38) back to GRCh37, and comparing
    against the curated interval in GRCh37 — which is also the project's canonical analytic
    plane (D-01, config genome_build: GRCh37).
    Verified: all 276 AFR windows lift with 0 failures (pyliftover, m3-r-ld env).
    Verified: start/end_grch38, core_*_grch38 and window_*_grch38 are populated for all
    276 AFR rows (0 blanks), and for all 153 NON-split rows core == window == region in
    GRCh38 — so one uniform mechanism is correct for split and non-split rows alike.

--- ⚠⚠ KNOWN-ANSWER CROSSWALK (RE-DERIVED 2026-08-05; SUPERSEDES the prior "12/12") ---

    THE PRIOR ORACLE WAS WRONG FOR SH2B3_12q24, AND THE "INDEPENDENT 12/12 REPRODUCTION"
    DID NOT CATCH IT — the blast-radius sweep re-implemented the SAME grch37-column
    mechanism and got the same wrong answer. Convergent reproduction of a bug is not
    verification. Treat the old table as void.

    THE TRAP, verified firsthand against config/ld_regions.tsv:
      All 18 subregions of m2_region_00040 carry an IDENTICAL start_grch37/end_grch37 of
      37,729,542-126,774,248 — the PARENT's ~89 Mb bounding box, copied verbatim into every
      subregion row (build_ld_region_manifest.py:585-587,650-653). ONLY the *_grch38
      columns (start/end, core_*, window_*) vary per subregion.
      => "smallest containing span" is a perfect 18-WAY TIE, and a lexicographic tie-break
         returns __sub00 regardless of physical position.
      => __sub00's REAL GRCh37 window is 37,857,542-45,792,298: ZERO bp overlap with SH2B3
         (chr12:111,400,000-112,000,000 GRCh37), ~66 Mb away. The previous specification
         would have pointed the Track A ANCHOR LOCUS at an unrelated window's LD panel.

    THE CORRECTED SELECTION RULE (this is what the builder must implement):
      1. Lift each AFR row's window_start_grch38 / window_end_grch38 -> GRCh37.
      2. CONTAINED = rows whose lifted window fully contains the curated GRCh37 interval.
      3. Rank CONTAINED by, in order:
           (a) CORE overlap with the curated interval, DESC   [core_*_grch38 lifted to GRCh37]
           (b) window span, ASC                               [tightest window]
           (c) min distance from the curated interval to either window edge, DESC
           (d) region_id lexicographic, ASC                   [determinism backstop]
      4. else PARTIAL: the row with the largest lifted-window intersection; record
         overlap_bp / overlap_frac.   5. else unmapped.
      HONEST NOTE: on today's data ONLY key (a) is ever load-bearing, and only for SH2B3 —
      every other curated region has EXACTLY ONE containing candidate (#cont == 1 below).
      (b)/(c)/(d) are determinism backstops, not active discriminators. Say so in the
      builder docstring rather than implying the ladder does more work than it does.

    RE-DERIVED ORACLE (lifted windows, physical containment; #cont = containing candidates):

      curated_region_id   chr  GRCh37 span              -> m2_region_id            #cont  status
      FTO_16q12           16   53800000-54400000        -> m2_region_00067           1    contained
      MC4R_18q21          18   56000000-56600000        -> m2_region_00078           1    contained
      SH2B3_12q24         12   111400000-112000000      -> m2_region_00040__sub14    2    contained  *** MOVED ***
      APOL1_22q12         22   36200000-36600000        -> m2_region_00105           1    contained
      PYHIN1_1q23          1   158000000-162000000      -> m2_region_00008           1    contained
      CXADR_F2RL1_6p21     6   10300000-11800000        -> m2_region_00142           1    contained
      BMI_5q13.3           5   72000000-76000000        -> m2_region_00135           1    contained
      BMI_Xq24             X   118000000-122000000      -> (none)                    0    unmapped
      9p21_CDKN2A          9   21000000-23000000        -> m2_region_00159           1    contained
      APOE_19q13          19   44000000-46000000        -> m2_region_00083           1    contained
      HLA_6p21             6   25000000-35000000        -> m2_region_00143           1    contained
      SLC2A9_urate         4   9000000-11000000         -> m2_region_00114           1    contained

    EXACTLY 1 OF 12 MOVED: SH2B3_12q24, __sub00 -> __sub14. The other 11 are unchanged AND
    are now re-confirmed by physical overlap rather than by the broken mechanism. Only
    SH2B3 maps to a SPLIT parent; the other 11 all resolve to non-split regions, which is
    why the defect was confined to one row — but it was confined to the ANCHOR row.

    THE sub14-vs-sub15 DECISION (a scientific choice — surfaced, not buried in a sort key):
      Both windows FULLY contain SH2B3, so containment cannot decide. Core overlap can:
        __sub14  core GRCh37 106,944,368-111,923,169  ->  523,169 bp of the 600,000 (87.2%)
        __sub15  core GRCh37 111,923,169-116,857,945  ->   76,831 bp of the 600,000 (12.8%)
      They partition the locus EXACTLY at the shared core boundary GRCh37 111,923,169
      (GRCh38 111,485,365) — SH2B3 STRADDLES it. RULE: maximize CORE overlap -> __sub14.
      WHY core overlap is the right primary key:
        1. It matches the manifest's OWN semantics. core_* / subregion_index define which
           subregion OWNS which variants, and stitch_subregions_to_rds.R de-dups on core
           ownership. Picking the subregion whose core owns most of the locus picks the
           panel the pipeline itself treats as authoritative for those variants.
        2. The independent secondary criterion AGREES, which is corroboration rather than
           coincidence: min distance from the locus to a window edge is 2,923,170 bp for
           __sub14 vs 2,520,858 bp for __sub15, so __sub14 also truncates LD less.
        3. Window span cannot decide: 10,978,802 vs 10,978,803 bp.
      ⚠ DISCLOSED LIMITATION, carry it to the SUMMARY: NEITHER core fully contains SH2B3.
      12.8% of the locus lives in __sub15's core, so __sub14's panel covers those variants
      only through its BUFFER — where a stitched parent's core-ownership de-dup would have
      assigned them elsewhere. This is a real property of using a subregion panel for a
      locus that straddles a core boundary. It is why the region-1 gate must check the
      REALIZED variant overlap/coverage rather than assume the bp arithmetic carries over.

--- VALIDATION PROTOCOL STATE ---
    .planning/phases/m3-aou-afr-ld-panel-build/validation/ has 4 subdirs, ALL containing
    only .gitkeep. The 4-check protocol has never been run. AOU-LD-PIPELINE.md:423 calls it
    "a hard gate for promoting the pipeline from dev to production".
    9.2 Check 2 = "AoU EUR vs 1000G EUR, mean entry-wise r >= 0.97 (MAF >= 0.05);
    >= 0.90 (MAF 0.01-0.05)".

--- THE STRUCK CRITERION (MEDIUM-7 / D-04b-03) ---
    `snakemake --dry-run --quiet` is UNSATISFIABLE pre-fire and must NOT appear in this
    plan. Re-proved firsthand at 676fe77:
        data/processed/ld_reference/ does not exist
        resolve_ld_path("FTO_16q12",      "AFR") -> RAISES FileNotFoundError
        resolve_ld_path("m2_region_00067","AFR") -> RAISES FileNotFoundError
    The crosswalk changes WHICH nonexistent path is requested, not whether one exists.
    REPLACEMENT: `snakemake --snakefile Snakefile --list` -- exits 0 today (verified), does
    not evaluate input lambdas, and proves what the dry-run was actually being used for:
    every rule file parses and every module-scope import resolves. If an executor ever
    feels the urge to `touch` a fake .rds to make a check pass: STOP and surface it.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1a: Layer A — the curated-to-M2 crosswalk (physical-overlap selection), the resolver argument, and BOTH test rewrites</name>
  <files>src/python/build_curated_m2_crosswalk.py, config/curated_to_m2_region_map.tsv, src/snakemake/rules/finemap.smk, tests/m3/test_curated_m2_crosswalk.py, tests/m3/test_occlusion_lockstep_wiring.py, tests/m3/test_ld_panel_resolver.py</files>
  <read_first>
    - The `⚠⚠ KNOWN-ANSWER CROSSWALK (RE-DERIVED 2026-08-05)` block in `<interfaces>` above.
      The PRIOR oracle is VOID. Do not use any table dated before 2026-08-05.
    - `.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md` §2 BLOCKER-2 /
      BLOCKER-3 / MEDIUM-6 / MEDIUM-7
    - `src/snakemake/rules/finemap.smk` — WHOLE FILE. Do not work from line numbers alone.
    - `Snakefile` :44-63 (how REGION_SAFE_TO_ID is really built — the root of Layer A)
    - `src/python/ld_panel.py` (resolve_ld_path; region_id and region_safe substitute
      independently; it RAISES when nothing exists on disk)
    - `config/regions_curated.csv` (all 12 rows) and `config/ld_regions.tsv` (header + the
      18 `m2_region_00040__sub*` rows — look at the grch37 columns and see them repeat)
    - `src/python/build_ld_region_manifest.py` :585-587, :650-653 (where the parent's
      bounding box gets copied into every subregion's grch37 columns — the root cause)
  </read_first>
  <behavior>
    RED-first. Module imported INSIDE each test body so pytest COLLECTS cleanly.

    === tests/m3/test_curated_m2_crosswalk.py ===

    T1.1 test_crosswalk_covers_every_curated_region — exactly one row per row of
      `config/regions_curated.csv` (12), keyed on `region_safe`.

    T1.2 test_core_overlap_outranks_window_span — synthetic. Two containing candidates: a
      TIGHTER window whose core barely overlaps the curated interval, and a WIDER window
      whose core contains it. The WIDER one must win. This pins the ranking ORDER (core
      overlap before span), which is the key the SH2B3 defect turned on.

    T1.3 test_partial_overlap_is_marked_not_silently_promoted — a curated interval no
      candidate contains but one overlaps gets `status=partial` with the overlap fraction.
      A partial match must never be presented as a clean containment.

    T1.4 test_chrx_region_is_unmapped — a chrX curated region (BMI_Xq24 in production) gets
      `m2_region_id` empty and `status=unmapped`. M2 is autosomes-only per D-M2-09.

    T1.5 test_selected_window_physically_overlaps_the_curated_interval — ⚠ THE CLASS-OF-BUG
      TEST. Parametrized over ALL 12 production rows. For every row with
      `status == "contained"`, independently recompute the selected M2 window's GRCh37
      coordinates and assert it FULLY CONTAINS the curated interval, and that the overlap
      equals the full curated span. This must NOT re-run the builder's own ranking — it
      validates the OUTPUT by physical geometry. A test that re-implements the selection
      cannot catch a wrong selection rule; that is precisely how the prior "12/12
      independent reproduction" reproduced the defect instead of finding it.

    T1.6 test_sh2b3_does_not_select_sub00 — ⚠ THE REGRESSION PIN for the exact defect.
      `SH2B3_12q24` must resolve to `m2_region_00040__sub14` and must NOT resolve to
      `m2_region_00040__sub00`. Assert BOTH directions, and assert in the same test that
      `__sub00`'s lifted GRCh37 window has ZERO overlap with the curated interval — so the
      test documents WHY `__sub00` is wrong, not merely that it is not chosen. Reverting to
      the grch37-column mechanism must fail this test.

    T1.7 test_sh2b3_tie_is_broken_on_core_overlap — assert the containing-candidate set for
      SH2B3 has exactly 2 members (`__sub14`, `__sub15`), that both fully contain the
      locus, and that the selected one is the one with the larger CORE overlap. This is the
      only place in production where a tie-break is load-bearing at all — pin it explicitly
      rather than letting it look incidental.

    T1.8 test_production_crosswalk_matches_the_rederived_oracle — parametrized over the 12
      rows of the RE-DERIVED table in `<interfaces>`. Secondary to T1.5/T1.6: an
      exact-value pin is only trustworthy because T1.5 validates the values geometrically.

    T1.9 test_crosswalk_is_deterministic — building twice over the same inputs produces a
      byte-identical TSV.

    T1.10 test_unmapped_region_resolver_argument_is_byte_identical_to_today — for an
      unmapped curated slug the `finemap.smk` expression falls back to
      `REGION_SAFE_TO_ID[region]`, so the value handed to `resolve_ld_path` is
      character-for-character today's. No frozen numerics can move.

    === The two test REWRITES ===
    Surgical edits, specified verbatim in STEPS 6 and 7. Both must end STRICTLY STRONGER,
    and STEP 7 adds a PERMANENT negative-control test.
  </behavior>
  <action>
    ORDER MATTERS. Do the steps in this order and commit at the marked points.

    ⓘ STEP NUMBERING: this task runs 0,1,2,3,6,7,8. **STEPS 4 and 5 are deliberately absent**
    — they were the `finemap.smk` shell wiring and the `--ld-file` thread, which moved to
    **Task 1b** in the 2026-08-05 split. The numbering of STEPS 6/7/8 is PRESERVED because
    the test rewrites are referenced by step number from `<interfaces>`, the changelog and
    the threat model. Nothing is missing; do not renumber.

    **STEP 0 — RED.** Write `tests/m3/test_curated_m2_crosswalk.py` first. Run it. Confirm
    every failure is call-time, not a collection error. Commit the RED.

    **STEP 1 — the crosswalk builder.** Create `src/python/build_curated_m2_crosswalk.py`:

        def build_curated_m2_crosswalk(regions_curated_csv, ld_regions_tsv, chain_path,
                                       out_tsv) -> dict

    ⚠ **DO NOT USE `start_grch37` / `end_grch37` FROM `config/ld_regions.tsv` FOR SELECTION.**
    They are the PARENT's bounding box, copied verbatim into every subregion row
    (`build_ld_region_manifest.py:585-587,650-653`), so all 18 subregions of
    `m2_region_00040` carry an identical ~89 Mb span. Selecting on them is an 18-way tie
    that lexicographically returns `__sub00` — a window with ZERO physical overlap with
    SH2B3, ~66 Mb away. Only the `*_grch38` columns vary per subregion.

    Algorithm:
    * read `config/regions_curated.csv` -> (region_safe = the slug with `.` and `/`
      replaced by `_`, matching `Snakefile:49`; curated_region_id; chr; start; end).
      These are GRCh37 (config `genome_build: GRCh37`, D-01).
    * read `config/ld_regions.tsv`, keep `ancestry == "AFR"` (all 276 unique ids appear
      under AFR).
    * **LIFT each candidate's `window_start_grch38` / `window_end_grch38` AND
      `core_start_grch38` / `core_end_grch38` to GRCh37** using
      `data/external/liftover/hg38ToHg19.over.chain.gz` via `pyliftover`. That is the ONLY
      chain in the repo — there is NO hg19->hg38 chain; do not assume one. ⚠ `pyliftover`
      is a RUNTIME DEPENDENCY of this config-building step: it is importable from
      `smoke_dev` today but is declared in NO tracked env yml for that env (only
      `envs/m3-r-ld.yml` and `envs/m3-aou-dev.yml` list it), so a future `smoke_dev`
      rebuild would break the crosswalk builder with no documented cause. Declare it in
      the env that actually runs this builder, and say so in the module docstring. Comparing in
      GRCh37 also keeps the analytic plane canonical. Verified: all 276 AFR windows lift
      with 0 failures. Normalize each lifted pair with `min`/`max` (the chain can invert).
      If a candidate's WINDOW fails to lift, exclude it and COUNT the exclusions in the
      returned dict — never silently drop.
      ⚠ ADDED 2026-08-05 (iteration-2 check, non-blocking hardening — all three paths are
      DEAD on today's data, which is exactly why they must be COUNTED rather than assumed):
      also count, in the returned dict and on stderr, (a) candidates whose CORE fails to
      lift while the WINDOW succeeds — fall back to the lifted window bounds for that
      candidate, but record it, because `core_overlap_bp` is the PRIMARY sort key and a
      silent window-substitution would distort the ranking that picks `__sub14`;
      (b) intervals that come back INVERTED (start > end) before min/max normalization;
      and (c) STRAND-INCONSISTENT lifts, where the start and end points lift to opposite
      strands. Measured on the real 276 AFR rows at plan time: (a) 0, (b) 0, (c) 5 — one
      of which, `m2_region_00008`, IS a production candidate (`PYHIN1_1q23`). That case was
      checked and does NOT distort the oracle (its naively-lifted window matches the
      manifest's own `start_grch37`/`end_grch37` for that non-split row, and PYHIN1 has a
      single containing candidate so no tie-break is exposed) — but normalizing it away
      SILENTLY would leave the next manifest regeneration with no signal at all.
    * CONTAINED = candidates whose lifted window satisfies `w0 <= curated_start` and
      `w1 >= curated_end`. Rank by, in order:
        (a) core overlap with the curated interval, DESC
        (b) window span, ASC
        (c) min(curated_start - w0, w1 - curated_end), DESC
        (d) `region_id` lexicographic, ASC
      `status="contained"`.
    * else PARTIAL: the candidate with the largest lifted-window intersection; record
      `overlap_bp` and `overlap_frac` (over the curated span). `status="partial"`.
    * else `m2_region_id=""`, `status="unmapped"`.
    * emit columns, in order: `region_safe, curated_region_id, chr, curated_start_grch37,
      curated_end_grch37, m2_region_id, m2_window_start_grch37, m2_window_end_grch37,
      m2_core_start_grch37, m2_core_end_grch37, window_overlap_bp, core_overlap_bp,
      overlap_frac, n_containing_candidates, status`. Sort by `region_safe`. `argparse`
      `main()`.
      The `m2_core_*` and `core_overlap_bp` columns are NOT decoration: they are the
      evidence for the selection, and T1.7 and the region-1 gate both read them.
    * In the module docstring, state honestly that on today's data only key (a) is ever
      load-bearing, and only for `SH2B3_12q24`; every other curated region has exactly ONE
      containing candidate. (b)/(c)/(d) are determinism backstops.
    * Record the sub14-vs-sub15 rationale (core ownership semantics; the corroborating
      edge-distance criterion; the disclosed straddle limitation) in the docstring, quoting
      the `<interfaces>` block. It is a scientific choice and must be readable at the call
      site, not buried in a sort key.

    Chromosome comparison MUST strip a `chr` prefix on BOTH sides
    (`_chrom_match_key` in `run_native_ld_panel.py` exists because a literal `==` against a
    `chr`-prefixed contig silently matched zero rows for 17 hours and banked 0/276).

    **STEP 2 — build and COMMIT `config/curated_to_m2_region_map.tsv`.** A reproducible
    config artifact, so it belongs in the repo (same convention as
    `config/region_id_mapping.tsv`). Diff against the RE-DERIVED oracle. If ANY row
    disagrees, the builder is wrong — fix the builder, never the oracle. In particular
    `SH2B3_12q24` MUST be `m2_region_00040__sub14`; if it comes out `__sub00` the builder
    is still reading the grch37 columns. Commit.

    **STEP 3 — `finemap.smk`, the resolver argument.**
    * Load the crosswalk once at module scope into `CURATED_TO_M2: dict[str, str]`,
      skipping rows whose `status == "unmapped"` or whose `m2_region_id` is empty. If the
      file is ABSENT, log a WARN and use `{}` — the DAG must still build on a fresh clone
      before the crosswalk has been generated.
    * Change ONLY line :174, to EXACTLY this text (the tests match it literally):

            region_id=CURATED_TO_M2.get(wildcards.region, REGION_SAFE_TO_ID[wildcards.region]),

    * Leave `region_safe=wildcards.region` (:177) unchanged — the 1kg / HGDP / UKBB tails
      template on it.
    * REPLACE the **CR-001 comment at :165-171** (not :117-123) with the corrected account:
      `REGION_SAFE_TO_ID` never performed the `FTO_16q12 -> m2_region_00067` translation it
      claimed; `config/curated_to_m2_region_map.tsv` performs it; and the crosswalk selects
      on LIFTED GRCh38 windows because the manifest's grch37 columns are parent-repeated.
    * ⚠ **DO NOT rewrite the boundary comment at :114-130.** It carries `m3-04b`,
      `m3-04c`, `occlusion_lockstep`, `consume`, and the ABSENCE of
      `SUPERSEDED-PENDING-REPLAN` — all asserted by
      `tests/m3/test_finemap_loader_contract.py:152-165`.
    * DO NOT touch `params.region_id` at :206, the sumstats/variants lambdas at :147-155,
      or the `shell:` block (that is Task 1b).

    **STEP 6 — REWRITE `tests/m3/test_occlusion_lockstep_wiring.py::test_params_region_id_is_untouched`
    (BLOCKER-2). Its own reviewed step; do not improvise.**

    The function body at :433-446 has THREE assertions. Replace the body with:

        src = _FINEMAP_SMK.read_text()

        # SURVIVES VERBATIM. This is the guard rail. Do not weaken, do not delete.
        assert "region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region]," in src, (
            "run_finemap.params.region_id must still translate the safe slug via "
            "REGION_SAFE_TO_ID"
        )

        # REPLACED, NOT RELAXED (m3-04c). The previous assertion pinned the exact
        # PRE-crosswalk literal that m3-04c is required to replace, so it forbade what
        # its own docstring documents as m3-04c's job. The replacement pins the STRONGER
        # post-condition: the resolver argument now routes through the curated->M2
        # crosswalk, with REGION_SAFE_TO_ID as the documented unmapped-region fallback.
        # Precedent for replace-don't-relax: 1a9d170, and m3-04b's own
        # test_production_boundary_documented.
        assert (
            "region_id=CURATED_TO_M2.get(wildcards.region, "
            "REGION_SAFE_TO_ID[wildcards.region])," in src
        ), (
            "run_finemap.input.ld_matrix's resolve_ld_path(region_id=...) argument must "
            "route through the curated->M2 crosswalk, falling back to REGION_SAFE_TO_ID "
            "for curated regions with no M2 counterpart"
        )

        # RE-DERIVED (m3-04c). The previous assertion was a brittle WHOLE-FILE
        # src.count("REGION_SAFE_TO_ID") == 3 that any comment rewrite moves. Counted on
        # CODE lines only and on the SUBSCRIPTED form, so prose cannot break it and a
        # third code-level use cannot sneak in.
        code = "\n".join(
            ln for ln in src.splitlines() if not ln.lstrip().startswith("#")
        )
        assert code.count("REGION_SAFE_TO_ID[wildcards.region]") == 2, (
            "expected exactly 2 CODE uses of REGION_SAFE_TO_ID[wildcards.region]: the "
            "crosswalk's unmapped-region fallback inside resolve_ld_path(region_id=...), "
            "and params.region_id"
        )

    Also update the docstring: m3-04c HAS NOW changed the sibling argument; this pin
    remains the guard rail that keeps the two edits from being conflated.
    VERIFIED: the code-only count is 2 both before and after the edit, so this assertion is
    a genuine invariant rather than a number tuned to make the suite green.

    **STEP 7 — REWRITE `tests/m3/test_ld_panel_resolver.py::test_finemap_smk_calls_resolver_with_both_kwargs`
    (BLOCKER-2b) AND ADD A PERMANENT NEGATIVE CONTROL.**

    Why the obvious fix is WRONG. The test's comment says "broaden to a non-greedy
    `[\s\S]*?` with explicit closing-paren anchoring." **Broadening alone silently makes
    the `region_id` assertion VACUOUS.** `finemap.smk:9` and `:12` mention
    ``resolve_ld_path()`` in the module docstring, so a non-greedy scan begins at line 9 —
    not at the real call site on line 173 — and runs to the nearest subsequent
    ``region_id\s*=``, which includes `params.region_id` at :206. Proved by sabotage
    (both kwargs stripped from the REAL call site): `[\s\S]*?` + `region_id` still returns
    **True**. The "closing-paren anchoring" half of the comment is the load-bearing half.

    7a. Add a module-level helper and rewrite the assertions to use it:

        def _resolve_ld_path_call_args(text):
            """Return the balanced-paren argument blocks of every real
            ``resolve_ld_path(...)`` CALL in *text*.

            The module docstring mentions ``resolve_ld_path()`` with EMPTY parens twice, so
            a plain regex scan starts there and can match a ``region_id=`` belonging to a
            different directive entirely (params.region_id). Walking balanced parens and
            keeping only NON-EMPTY blocks isolates the one true call site, and tolerates
            the nested parens the m3-04c crosswalk introduces.
            """
            blocks = []
            for m in re.finditer(r"resolve_ld_path\s*\(", text):
                i = m.end() - 1
                depth = 0
                for j in range(i, len(text)):
                    if text[j] == "(":
                        depth += 1
                    elif text[j] == ")":
                        depth -= 1
                        if depth == 0:
                            inner = text[i + 1:j]
                            if inner.strip():
                                blocks.append(inner)
                            break
            return blocks

    Then, in `test_finemap_smk_calls_resolver_with_both_kwargs`, replace both
    `re.search(r"resolve_ld_path\s*\([^)]*<kw>\s*=", text, re.DOTALL)` assertions with:

        blocks = _resolve_ld_path_call_args(text)
        assert len(blocks) == 1, (
            f"expected exactly ONE resolve_ld_path(...) call site in finemap.smk, "
            f"found {len(blocks)}"
        )
        args = blocks[0]
        assert re.search(r"\bregion_id\s*=", args), (
            "finemap.smk's resolve_ld_path call is missing the region_id= kwarg"
        )
        assert re.search(r"\bregion_safe\s*=", args), (
            "finemap.smk's resolve_ld_path call is missing region_safe= kwarg — CR-001 "
            "regression risk: without it the resolver's back-compat default re-introduces "
            "the same-value substitution bug for the 1kg/HGDP/UKBB tails of the chain."
        )

    Update the explanatory comment to record that the call site now DOES contain nested
    parentheses (the crosswalk `.get`) AND that the docstring mentions are why a regex
    cannot be trusted here.

    7b. ⚠ **ADD A PERMANENT NEGATIVE-CONTROL TEST** — `test_kwarg_assertion_is_not_vacuous`.
    Read `finemap.smk`, build an in-memory SABOTAGED copy with the kwarg names stripped
    from the REAL call site only (leave the docstring and `params.region_id` intact), and
    assert the extracted block does NOT match `\bregion_id\s*=` / `\bregion_safe\s*=`.
    Do it for both the strip-both and strip-`region_safe`-only variants. This makes "the
    assertion can still fail" a CI-enforced property instead of a claim.
    VALIDATED during planning on four inputs:

        input                        n_blocks  region_id  region_safe
        HEAD                            1        True       True
        post-crosswalk                  1        True       True
        sabotaged (both stripped)       1        False      False
        sabotaged (region_safe only)    1        True       False

    Do NOT weaken either assertion in any other way — both kwargs must still be required.
    ⛔ **Do not ship a pattern whose only evidence is that it returns True.**

    **STEP 8 — GREEN for this task.** Run `tests/m3`.
    ⚠ **If ANY test outside the two named in STEPS 6 and 7 fails, STOP and surface it. Do
    NOT edit it.** Those two are the only pre-authorized test edits in this plan. A third
    failing test means an unmodelled coupling, and the project's standing rule is that a
    surprising RED is a finding, not an obstacle.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3 -q &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile --list &gt; /dev/null &amp;&amp; grep -qF 'region_id=CURATED_TO_M2.get(wildcards.region, REGION_SAFE_TO_ID[wildcards.region]),' src/snakemake/rules/finemap.smk &amp;&amp; grep -qF 'region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],' src/snakemake/rules/finemap.smk &amp;&amp; grep -q 'm2_region_00040__sub14' config/curated_to_m2_region_map.tsv &amp;&amp; ! grep -q 'm2_region_00040__sub00' config/curated_to_m2_region_map.tsv &amp;&amp; grep -q '_resolve_ld_path_call_args' tests/m3/test_ld_panel_resolver.py &amp;&amp; grep -q 'test_kwarg_assertion_is_not_vacuous' tests/m3/test_ld_panel_resolver.py &amp;&amp; ! grep -q 'SUPERSEDED-PENDING-REPLAN' src/snakemake/rules/finemap.smk</automated>
  </verify>
  <acceptance_criteria>
    - `tests/m3` reports **0 failed**, **>= 496 passed**, **skips <= 31**.
    - `config/curated_to_m2_region_map.tsv` exists with 13 lines (header + 12) and every row
      matches the RE-DERIVED oracle.
    - `grep -c 'm2_region_00040__sub14' config/curated_to_m2_region_map.tsv` is 1 AND
      `grep -c 'm2_region_00040__sub00' config/curated_to_m2_region_map.tsv` is **0**.
      ⛔ `__sub00` appearing means the builder is still reading the parent-repeated grch37
      columns and the anchor locus is pointed 66 Mb off target.
    - For every `status == "contained"` row, `window_overlap_bp` equals
      `curated_end_grch37 - curated_start_grch37` (full containment, verified geometrically).
    - `awk -F'\t' 'NR>1 && $NF=="unmapped"' config/curated_to_m2_region_map.tsv` returns
      exactly the `BMI_Xq24` row.
    - The SH2B3 row has `n_containing_candidates == 2` and the larger `core_overlap_bp`
      (523,169 of 600,000) of the two.
    - `test_kwarg_assertion_is_not_vacuous` EXISTS and PASSES.
    - `grep -cF 'region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],'
      src/snakemake/rules/finemap.smk` is exactly 1 (`params.region_id` untouched).
    - Building the crosswalk twice yields byte-identical files (`md5sum` match).
    - `snakemake --snakefile Snakefile --list` exits 0.
      ⛔ `snakemake --dry-run` is NOT a criterion — unsatisfiable pre-fire (MEDIUM-7).
    - Exactly TWO existing tests were edited: `test_params_region_id_is_untouched` and
      `test_finemap_smk_calls_resolver_with_both_kwargs` (plus ONE net-new negative control).
  </acceptance_criteria>
  <done>
    The path Snakemake declares is the RIGHT one, selected by PHYSICAL overlap in a single
    coordinate build rather than by a parent-repeated column that silently tied 18 ways.
    `SH2B3_12q24` — the Track A anchor — resolves to the subregion whose core actually owns
    the locus, and a regression test pins that the 66-Mb-off `__sub00` can never come back.
    Both tests that contradicted this plan are stronger, the `params.region_id` guard rail
    is intact, and neither rewrite left an assertion that cannot fail.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 1b: Layer B — the --ld-file read-path thread in run_susie_rss.R, the shell wiring, and Path-2 observability</name>
  <files>src/legacy/region_analysis/scripts/run_susie_rss.R, src/snakemake/rules/finemap.smk, tests/m3/test_ld_read_path.py</files>
  <read_first>
    - `DEC-2026-08-05-m3-ld-read-path` in `.planning/DECISIONS.md` (LOCKED; the
      promote/symlink rule and the per-ancestry `ld_dir` are REJECTED — do not substitute)
    - `.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md` headline +
      BLOCKER-1 / HIGH-2
    - `src/legacy/region_analysis/scripts/run_susie_rss.R` :69-232 (the loader), :234-250
      (option_list), :290-300 (flag init), :419-431 (Path 2), :466-483 (identity fallback),
      :528-549 (the result list)
    - `src/snakemake/rules/finemap.smk` :218-237 (the shell block — the ONLY part this task
      touches; Task 1a owns the `input:` block)
    - `tests/m3/test_stitch_subregions_to_rds.py` :49-250 (`_require_m3_r_toolchain`,
      `_loader_functions_only`) and `tests/m3/test_finemap_loader_contract.py` (the shape
      to copy for the behavioural test)
  </read_first>
  <behavior>
    RED-first. `tests/m3/test_ld_read_path.py`. The decision requires proving
    `resolved == what-the-script-opens`. A green DAG is NOT evidence. Two halves: a STATIC
    half pinning that the shell passes the declared artifact, and a BEHAVIOURAL half that
    runs the REAL R loader.

    T2.1 test_run_finemap_shell_passes_the_declared_ld_matrix — STATIC. Slice `finemap.smk`
      to the `run_finemap` rule's `shell:` block and assert
      `re.search(r"--ld-file\s+\{input\.ld_matrix\}", shell_block)`. Assert the VALUE token
      is exactly `{input.ld_matrix}` — not `{params.ld_dir}`, not a rebuilt string. This is
      the one assertion that would have caught BLOCKER-1 at m3-W3-T2.

    T2.2 test_ld_file_option_is_declared — STATIC. `run_susie_rss.R`'s `option_list`
      contains `make_option("--ld-file"`, and `load_ld_matrix`'s signature accepts an
      `ld_file` argument.

    T2.3 test_loader_opens_the_declared_file_not_the_reconstructed_path — BEHAVIOURAL, the
      real acceptance test. Using `_require_m3_r_toolchain` + `_loader_functions_only`:
      place a real `.rds` (with `$R` and `$variants` overlapping the subset) at
      `{tmp}/ld_reference/AFR_aou/m2_region_00067.rds`; ALSO create
      `{tmp}/ld_reference/AFR/` as an EXISTING but EMPTY directory (so the `ld_dir` guard
      passes and the reconstruction genuinely has somewhere to look and finds nothing).
      Call `load_ld_matrix(ld_dir, "AFR", "FTO_16q12", subset, ld_file = <the AFR_aou path>)`.
      ASSERT `res$source` equals that exact AFR_aou path AND `res$R` is NOT NULL.
      This FAILS on today's code (no such argument), which is the RED.

    T2.4 test_absent_ld_file_still_reconstructs_from_ld_dir — BEHAVIOURAL. Same fixture but
      the `.rds` sits at `{ld_dir}/AFR/FTO_16q12.rds` and `ld_file = NULL`. Assert
      `res$source` is that path. Pins the fallback so no existing caller breaks.

    T2.5 test_ld_file_works_when_ld_dir_is_absent — BEHAVIOURAL. THE TRAP at
      `run_susie_rss.R:74-76`. Pass `ld_dir = NULL` (and separately a nonexistent dir) with
      a valid `ld_file`. Assert the matrix LOADS and `res$status` is NOT `"ld_dir_missing"`.

    T2.6 test_both_absent_returns_the_byte_identical_legacy_status — BEHAVIOURAL. `ld_dir`
      nonexistent AND `ld_file = NULL` -> `res$R` NULL and `res$status ==
      "ld_dir_missing"`, character-for-character. Pins that the guard's legacy contract is
      preserved, not merely bypassed.

    T2.7 test_path2_ld_overlap_zero_fallback_is_observable_and_read — STATIC on
      `run_susie_rss.R` + `finemap.smk` (HIGH-2). Assert: `ld_overlap_zero_fallback` is
      initialized `FALSE` alongside `variant_catalog_fallback`; the `ld_overlap == 0`
      branch sets BOTH `variant_catalog_fallback <- TRUE` and
      `ld_overlap_zero_fallback <- TRUE`; both appear in the success result list; and
      `finemap.smk`'s estimate_s log line READS `ld_overlap_zero_fallback`.
      HONEST LIMITATION, state it in the test docstring: exercising Path 2 end-to-end needs
      the whole script (sumstats + regions csv + policy + variant list), so this is pinned
      at source level. The project already uses source-level assertions for Snakemake
      directives with the same documented rationale.

    T2.8 test_declared_and_opened_paths_are_both_recorded_in_the_output_json — STATIC.
      `run_susie_rss.R`'s success result carries BOTH `ld_matrix` (the path OPENED, already
      present at :538) and a NEW `ld_file_declared` (the path Snakemake DECLARED). This is
      what makes `resolved == opened` checkable per region after the fire.
  </behavior>
  <action>
    **STEP 0 — RED.** Write `tests/m3/test_ld_read_path.py` first. Confirm T2.3-T2.6 fail
    because `load_ld_matrix` has no `ld_file` argument — NOT because the toolchain is
    missing. `/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript` exists on this
    node, so `_require_m3_r_toolchain` will NOT skip. Commit the RED.

    **STEP 1 — `run_susie_rss.R`: the `--ld-file` thread.** This is the LOCKED remedy
    (`DEC-2026-08-05-m3-ld-read-path`). Do NOT substitute a promote/symlink rule or a
    per-ancestry `ld_dir`; both were explicitly REJECTED.

    1a. `option_list` (after the `--ld-dir` entry at :241) — add:
        `make_option("--ld-file", type = "character", default = NULL,`
        with help text stating: the resolved LD `.rds` Snakemake declared as
        `input.ld_matrix`; AUTHORITATIVE when readable; `--ld-dir` reconstruction is the
        back-compat fallback. Accessed as ``opt$`ld-file` ``.

    1b. `load_ld_matrix` signature at :73 becomes
        `function(ld_dir, ancestry, region_id, subset, ld_file = NULL)`.
        `ld_file` LAST with a default, so any positional caller is unaffected.

    1c. **Replace the guard at :74-76.** This is the trap: as written it bails whenever
        `ld_dir` is absent, even with a perfectly good `--ld-file`. New shape:

            have_ld_file <- !is.null(ld_file) && nzchar(ld_file) && file.exists(ld_file)
            have_ld_dir  <- !is.null(ld_dir) && ld_dir != "" && file.exists(ld_dir)
            if (!have_ld_file && !have_ld_dir) {
              return(list(R = NULL, source = NULL, status = "ld_dir_missing"))
            }

        The `status` string stays **byte-identical** for the both-absent case so nothing
        downstream moves.

    1d. **Candidate construction at :123-127.** Build the dir candidates ONLY when
        `have_ld_dir` (R semantics: `file.path(NULL, ...)` returns `character(0)` and
        `file.path("", ...)` returns an absolute `/AFR/...`, both wrong), then put the
        declared file FIRST:

            dir_candidates <- if (have_ld_dir) unique(c(
              file.path(ld_dir, ancestry, paste0(region_id, ".rds")),
              file.path(ld_dir, ancestry, paste0(safe_id,   ".rds"))
            )) else character(0)
            candidates <- unique(c(if (have_ld_file) ld_file else character(0),
                                   dir_candidates))

        `ld_file` FIRST is what makes `resolve_ld_path` the single source of truth; the
        `ld_dir` reconstruction survives strictly as the fallback the decision preserves.
        Leave the rest of the loop (:134-215) untouched.

    1e. **Call site at :421** becomes
        ``load_ld_matrix(opt$`ld-dir`, opt$ancestry, opt$region, subset, ld_file = opt$`ld-file`)``.
        Leave ``opt$`ld-dir` `` at :368, :400 and :537 exactly as they are.

    1f. **HIGH-2, same pass.** Initialize `ld_overlap_zero_fallback <- FALSE` immediately
        after `variant_catalog_fallback <- FALSE` (:298). Inside the `ld_overlap == 0 &&
        used_variant_catalog && attempt == 1` branch (:423-428) add BOTH
        `variant_catalog_fallback <- TRUE` and `ld_overlap_zero_fallback <- TRUE`. Add both
        to the success result list (:528-549). **Do NOT change Path 2's science behaviour**
        — it still reverts to `subset_base` and retries exactly once. Only observability
        changes.

    1g. Add ``ld_file_declared = opt$`ld-file` `` to the success result list, beside the
        existing `ld_matrix = ld_source`. Declared + opened, side by side, per region.
        Additive JSON keys are safe: `summarize_finemap_results.py` reads with `.get()`
        against a fixed `FIELDNAMES` list (verified).

    **STEP 2 — `finemap.smk`, the shell block ONLY.** In the `Rscript` invocation
    (:221-232), add ONE line immediately after `--ld-dir {params.ld_dir} \`:

            --ld-file {input.ld_matrix} \

    Purely additive. This is the line whose absence made `input.ld_matrix` a DAG
    declaration only.

    Also extend the estimate_s log one-liner at :236 so the new flags are actually READ:
    add `'ld_matrix', d.get('ld_matrix'), 'ld_file_declared', d.get('ld_file_declared'),
    'variant_catalog_fallback', d.get('variant_catalog_fallback'),
    'ld_overlap_zero_fallback', d.get('ld_overlap_zero_fallback')` to its `print(...)`.
    No f-string braces — only Snakemake's `{{}}` placeholders — so the rule shell stays
    valid. This turns every region's log into a `resolved == opened` receipt.

    ⚠ **DO NOT touch the `input:` block.** Task 1a owns `:132-179`. This task owns
    `:218-237`. Same file, disjoint regions, sequential execution — but if `git diff` shows
    this task modifying the `input:` block, back it out.

    **STEP 3 — GREEN for this task.** Run `tests/m3`. Same STOP rule: no test outside the
    two pre-authorized in Task 1a may be edited.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3 -q &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile --list &gt; /dev/null &amp;&amp; grep -qF -- '--ld-file {input.ld_matrix}' src/snakemake/rules/finemap.smk &amp;&amp; grep -qF 'ld-file' src/legacy/region_analysis/scripts/run_susie_rss.R &amp;&amp; grep -qF 'ld_file_declared' src/legacy/region_analysis/scripts/run_susie_rss.R &amp;&amp; grep -qF 'ld_overlap_zero_fallback' src/legacy/region_analysis/scripts/run_susie_rss.R &amp;&amp; grep -qF 'ld_overlap_zero_fallback' src/snakemake/rules/finemap.smk &amp;&amp; grep -qF 'ld_dir_missing' src/legacy/region_analysis/scripts/run_susie_rss.R</automated>
  </verify>
  <acceptance_criteria>
    - `tests/m3` reports 0 failed, >= 496 passed, skips <= 31.
    - The four BEHAVIOURAL read-path tests (T2.3-T2.6) **RAN** — passed, not skipped.
      `/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript` exists, so a skip here
      means the harness was mis-wired.
    - `grep -cF -- '--ld-file {input.ld_matrix}' src/snakemake/rules/finemap.smk` is
      exactly 1.
    - `run_susie_rss.R` still returns the byte-identical `"ld_dir_missing"` status for the
      both-absent case (pinned by T2.6).
    - `git diff` for this task shows NO change to `finemap.smk`'s `input:` block.
    - `snakemake --snakefile Snakefile --list` exits 0.
  </acceptance_criteria>
  <done>
    `resolved == what-the-script-opens` is PROVEN, not asserted: `run_finemap`'s shell
    passes `{input.ld_matrix}` as `--ld-file`, and the REAL R loader has been observed
    opening that exact artifact in preference to the `ld_dir` reconstruction, for a path
    (`AFR_aou/`) that reconstruction can never reach. The `--ld-dir` fallback still works,
    the both-absent contract is unchanged, and the `ld_overlap == 0` revert is no longer
    invisible.
  </done>
</task>

<task type="auto">
  <name>Task 1c: Full-suite GREEN, the frozen-contract gate, and the disclosed numerics change</name>
  <files>src/snakemake/rules/finemap.smk</files>
  <read_first>
    - the SUMMARYs / diffs produced by Tasks 1a and 1b
    - `config/pipeline.yaml` `ld_panel.pin` block (the hold switch named below)
  </read_first>
  <action>
    Depends on Tasks 1a AND 1b. Small by design: this is the join point where the two
    halves are checked TOGETHER, because neither alone delivers reachability.

    1. Run the FULL `tests/m3` suite and confirm 0 failed, >= 496 passed, <= 31 skipped,
       with the four behavioural read-path tests PASSED (not skipped).

    2. Confirm the frozen-contract gate: `git diff --exit-code 676fe77 --` clean for
       `plink_ld_to_npz.py`, `ld_npz_to_rds.R`, `condition_ld_matrix.py` and the four m3-07
       modules. m3-06 stays HELD: no `condition_ld_matrix` import, no NaN->0 revival.

    3. Confirm exactly TWO pre-existing tests were edited across 1a+1b
       (`test_params_region_id_is_untouched`, `test_finemap_smk_calls_resolver_with_both_kwargs`)
       plus ONE net-new negative control. Any other modified pre-existing test is a STOP.

    4. **RECORD, do not silently apply, the scientific consequence.** Add a comment above
       the crosswalk load in `finemap.smk` stating plainly: the first curated AFR region
       whose `AFR_aou/.rds` exists will switch from the `AFR_1kg` panel to the AoU AFR
       panel and its fine-mapping numerics WILL change. That is the intended purpose of M3
       (1000G AFR n=661 is the miscalibration this phase exists to fix), but it is a
       disclosable analysis change. Name `config/pipeline.yaml ld_panel.pin.AFR` as the
       switch that holds the fit at a specific source while the change is disclosed.

       In the SAME comment, record the SH2B3 straddle caveat: `SH2B3_12q24` maps to
       `m2_region_00040__sub14`, whose CORE owns 523,169 of the 600,000 bp locus (87.2%);
       the remaining 12.8% sits in `__sub15`'s core and is covered only through `__sub14`'s
       buffer. Point at the region-1 gate (Task 3 STEP A) as where the realized variant
       overlap/coverage is checked.

    5. Carry both disclosures into the plan SUMMARY.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3 -q &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile --list &gt; /dev/null &amp;&amp; grep -qF -- '--ld-file {input.ld_matrix}' src/snakemake/rules/finemap.smk &amp;&amp; grep -qF 'region_id=CURATED_TO_M2.get(wildcards.region, REGION_SAFE_TO_ID[wildcards.region]),' src/snakemake/rules/finemap.smk &amp;&amp; grep -qF 'region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],' src/snakemake/rules/finemap.smk &amp;&amp; grep -q 'ld_panel.pin.AFR' src/snakemake/rules/finemap.smk &amp;&amp; grep -q 'sub14' src/snakemake/rules/finemap.smk &amp;&amp; test ! -e src/python/validate_bundle_sizes.py &amp;&amp; git diff --exit-code 676fe77 -- src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R src/python/condition_ld_matrix.py src/python/occlusion_span_filter.py src/python/occlusion_manifest.py src/python/occlusion_present_rate_scan.py src/python/drop_occluded_from_sumstats.py</automated>
  </verify>
  <acceptance_criteria>
    - `tests/m3`: 0 failed, >= 496 passed, <= 31 skipped; the four behavioural read-path
      tests PASSED, not skipped.
    - `git diff --exit-code 676fe77 --` clean for the three frozen contracts and the four
      m3-07 modules.
    - `src/python/validate_bundle_sizes.py` still does NOT exist.
    - `finemap.smk` carries BOTH disclosures (the `AFR_1kg -> AFR_aou` numerics switch with
      `ld_panel.pin.AFR` named as the hold, and the SH2B3 `__sub14` straddle caveat).
    - `git diff --stat` on `tests/` shows exactly two pre-existing test functions modified
      plus one net-new negative control.
  </acceptance_criteria>
  <done>
    Both layers are green together, the frozen surface is provably untouched, and the two
    disclosable scientific consequences — the panel switch and the SH2B3 core straddle —
    are recorded in code and routed to the SUMMARY rather than absorbed silently.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: De-stale the ingest/convert rules, build the egress request plan on the existing helper, and record the two protocol redefinitions</name>
  <files>src/snakemake/rules/m3_ingest_aou_ld.smk, src/snakemake/rules/m3_convert_npz_rds.smk, src/python/plan_ld_egress.py, .planning/amendments/m3-egress-and-validation-protocol-addendum.md, .planning/amendments/aou-egress-audit-log.md, .planning/ROADMAP.md, tests/m3/test_m3_ingest_convert_destale.py</files>
  <read_first>
    - src/snakemake/rules/m3_ingest_aou_ld.smk (WHOLE FILE)
    - src/snakemake/rules/m3_convert_npz_rds.smk (WHOLE FILE)
    - src/python/ld_egress_bundle.py (WHOLE FILE — the helper to REUSE; its docstring :9-15
      carries the EGRESS_CAP_GB provenance correction verbatim)
    - .planning/amendments/AOU-LD-PIPELINE.md §7 (export protocol) and §9 (validation
      protocol, especially §9.2)
    - .planning/amendments/aou-egress-audit-log.md (it declares itself APPEND-ONLY at line 9)
    - .planning/ROADMAP.md lines 200, 211, 212
  </read_first>
  <behavior>
    RED-first. `tests/m3/test_m3_ingest_convert_destale.py` — static rule-file contract
    tests (read the `.smk` text and assert on it) plus behavioural tests for the planner:

    T3.1 test_subregion_ids_match_the_region_wildcard — the `region_id` wildcard pattern in
      BOTH rule files matches `m2_region_00040__sub00` AND `m2_region_00001`. Drive it from
      the REAL manifest: assert every one of the 276 unique ids in `config/ld_regions.tsv`
      matches the compiled pattern. Today `r"m2_region_\d{5}"` fails for 123 of them.

    T3.2 test_ingest_is_afr_only — the ancestry wildcard constraint no longer admits EUR
      (both blocks), and the aggregate `expand` no longer iterates EUR.

    T3.3 test_eur_aou_convert_rule_is_retired — `build_ld_rds_aou_eur` is absent from
      `m3_convert_npz_rds.smk`, and the file carries a comment naming `EUR_ukbb_pub` as the
      reason.

    T3.4 test_egress_plan_uses_the_shipped_helper — `plan_ld_egress` imports
      `plan_egress_bundles` from `ld_egress_bundle` and defines no bin-packer of its own
      (assert `plan_egress_bundles` appears in the module source and no local function name
      contains `bin_pack` / `split_bundle`).

    T3.5 test_egress_plan_groups_by_chromosome_and_splits_over_cap — a synthetic size table
      with one 60 GB chromosome yields `chrN_a` / `chrN_b` sub-bundles, each at or under the
      cap; a 10 GB chromosome yields a single `chrN`.

    T3.6 test_no_validate_bundle_sizes_module — `src/python/validate_bundle_sizes.py` does
      NOT exist. The stale plan asked for it; its function shipped at `ade6066`.

    T3.7 test_egress_audit_log_ruling_text_is_intact — the 2026-04-28 HARD GATE ruling
      string is still present byte-for-byte, and the append-only declaration at line 9 is
      unchanged.
  </behavior>
  <action>
    1. RED suite first; commit; confirm failures.

    2. `src/snakemake/rules/m3_ingest_aou_ld.smk`:
       * `ancestry=r"AFR"` in BOTH `wildcard_constraints` blocks (:120 and :321);
         `expand(..., ancestry=["AFR"], ...)` at :195-204 -> at most 22 flags, not 44.
       * `region_id=r"m2_region_\d{5}(__sub\d{2})?"` (:322).
       * the inventory `run:` block filters the manifest on `ancestry == "AFR"` and reports
         the 276-region scope in its error strings.
       * rewrite the module docstring: the producer is `src/python/run_native_ld_panel.py`
         (native plink1.9, Hail-free, single AoU Cloud Analysis VM) writing per-region
         `.npz` DIRECTLY to `gs://<bucket>/ld/AFR_aou/{region_id}.npz`. Delete the `bm/`
         BlockMatrix-shard language (Path A.3 is RETIRED) and the "322 rows" comment at :74
         and the "all 322 cells" comment at :289.
       * KEEP the per-chromosome flag as the arrival gate: the egress runs over multiple
         weeks and partial arrival must still let partial conversion proceed.

    3. `src/snakemake/rules/m3_convert_npz_rds.smk`:
       * widen `region_id` identically at :103 and :145.
       * RETIRE `build_ld_rds_aou_eur` (:122-158). Replace the rule with a comment block
         recording why: m3-02e Move 2 made `EUR_ukbb_pub` the `ld_panel.EUR` chain head
         (public UKBB 337k, `$0` compute), so `data/interim/aou_ld_exports/EUR_aou/` will
         never be populated and the rule could only ever fail on a missing input. Reference
         `src/snakemake/rules/m3_public_eur_ld.smk` as the live EUR producer. Verified: the
         rule has no code or test references outside `.planning` docs.
       * update the module docstring accordingly.

    4. Create `src/python/plan_ld_egress.py` — a THIN CLI over the shipped helper:
       * `--sizes-tsv` (columns `region_id`, `chr`, `bytes`; produced from a
         `gsutil ls -l gs://<bucket>/ld/AFR_aou/*.npz` capture — that command belongs in the
         Task 3 gate, not here), `--cap-gb` (default `ld_egress_bundle.EGRESS_CAP_GB`),
         `--out`.
       * call `plan_egress_bundles` directly. Do NOT reimplement grouping or splitting.
       * emit `.planning/amendments/m3_egress_plan_AFR.tsv` with one row per bundle:
         `bundle_id, chr, n_cells, total_bytes, total_gb, region_ids`, plus a trailing
         summary of `n_bundles_over_cap` and `chromosomes_split`.

    5. Create `.planning/amendments/m3-egress-and-validation-protocol-addendum.md`. Three
       recorded decisions, each with its evidence:

       **(a) Egress UNIT redefinition.** The stale plan assumed a per-chromosome bundle
       OBJECT that could be sized and split. The real producer writes per-region `.npz`
       DIRECTLY to `gs://<bucket>/ld/AFR_aou/{region_id}.npz`
       (`run_native_ld_panel.py:922-938`); no stage exists at which a "chr1 AFR bundle"
       object exists. The bundle is therefore a REQUEST-LEVEL grouping of object URIs: at
       most 22 AFR chromosome groups, plus within-chromosome size splits, transferred with
       `gsutil -m cp` per group. Scope moves from 44 bundles (22 chr x 2 ancestries) to at
       most 22 (AFR only; EUR is the public UKBB 337k panel at `$0` on NC State).

       **(b) EGRESS_CAP_GB provenance correction.** 50 GB is a CONSERVATIVE PROJECT WORKING
       CEILING, NOT a documented hard AoU API limit (`ld_egress_bundle.py:9-15`). AoU's real
       mechanism is an alert threshold plus manual relaxation at egress-request time; the
       real number is confirmed on the first export. The stale m3-04 plan treated it as
       hard fact.

       **(c) REQ-AOU-LD-VALIDATION Check 2 redefinition.** AOU-LD-PIPELINE.md §9.2 requires
       "AoU EUR vs 1000G EUR entry-wise r >= 0.97". There will be no AoU EUR panel, so the
       check is STRUCTURALLY UNRUNNABLE. It is redefined into three parts, which together
       preserve a check that can actually FAIL:

       * **2a (HARD GATE, replaces §9.2).** *Code-path equivalence on a public substrate.*
         Run `run_native_ld_panel.process_region` over the public 1000G plink files already
         on disk (the LDSC `1000G_EUR_Phase3_plink` set), for 2-3 curated-overlapping
         windows, and compare the resulting `.npz` LD against an independent
         `plink1.9 --r square bin4 --keep-allele-order` computed directly on the same
         window. PASS: identical variant ordering and entry-wise `max |delta| <= 1e-6`.
         This validates the EXACT estimator plus IO path that produces the AFR panel — the
         same `--keep-allele-order`, the same `.ld.bin` reader, the same `.npz` writer and
         the same `lower_triangular` flag. `$0`, no perimeter, and it can fail for a real
         code reason. Honest limitation, to be stated in the memo: it validates the CODE,
         not the AoU substrate or the cohort QC.
       * **2b (REPORTED, explicitly NOT thresholded).** *AoU AFR vs 1000G AFR entry-wise
         Pearson r*, on shared variants at the validation regions, stratified by MAF. A
         threshold here would be scientifically wrong: 1000G AFR (n=661, continental
         African) and AoU AFR (n~73k, admixed African-American) differ in both population
         and n, and that divergence is the entire rationale for M1a
         (AOU-LD-PIPELINE.md §1). A LOW r is the expected and desired finding. Reporting
         the number IS the deliverable.
       * **2c (SANITY, not a hard gate).** *EUR_ukbb_pub vs 1000G EUR entry-wise r* at the
         same regions, MAF >= 0.05, expected r >= 0.90. This validates the EUR chain head
         actually shipped. The original 0.97 bar is inappropriate here: both panels are
         external and differ in n (337k vs 503).

       State plainly that §9 is a PRE-REGISTERED hard gate, so this redefinition requires an
       **OSF amendment-update posting before any redefined check is cited as passed** —
       mirroring the m3-07a gate discipline (draft by agent, POST by Carter, record the file
       GUID). Route it through the Task 3 gate (STEP F).

    6. APPEND (never rewrite) a scope-correction section to
       `.planning/amendments/aou-egress-audit-log.md`. The file declares itself append-only
       at line 9 and its 2026-04-28 HARD GATE ruling text must remain byte-intact. The new
       section records: the M3 egress scope stated in the header (44 bundles, 22 chr x 2
       ancestries) is superseded to at most 22 AFR chromosome groups; the reason (m3-02e
       cost re-architecture: EUR moved to the public UKBB 337k panel, AFR moved to native
       plink); and a pointer to the protocol addendum. Do NOT edit the header line itself.

    7. `.planning/ROADMAP.md`:
       * REPLACE line 211's `m3-04` entry with:

             - [ ] m3-04b-W4-occlusion-catalog-and-consume-seam-PLAN.md + m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md
               — Wave 4 REPLANNED 2026-08-03, m3-04c RE-PLANNED AGAIN 2026-08-05 around
               DEC-2026-08-05-m3-ld-read-path. `m3-04-W4-production-and-egress-PLAN.md` is
               RETAINED AS HISTORY and is STALE on 9 axes (Hail/BlockMatrix substrate; 322
               cells vs 276 regions; symmetric AFR+EUR AoU build vs AFR-only + public UKBB
               EUR; 160-260 cluster-h / $5-10k vs ~263 VM-h / ~$385-1,084; per-chromosome
               bundle OBJECTS that never exist; the unreachable `m3_dev_complete.flag` gate;
               total silence on the occlusion lockstep; stale downstream ingest/convert
               rules; and a curated-to-M2 region crosswalk that never existed). It was NEVER
               EXECUTED — 5 of its 6 `files_modified` paths do not exist. The replan
               CONSUMES m3-02e's AFR-native `.npz` plus the public EUR `.rds`; it does not
               rebuild LD.
               **m3-04b** (autonomous, `$0`, NC State): occlusion catalog assembler giving
               the four zero-caller m3-07b/07c functions a production caller, plus the
               lockstep consume seam wiring occlusion-filtered AFR sumstats AND variant
               lists into `run_finemap` — discharging the m3-07c disclosed deferral.
               **m3-04c** (`autonomous:false`): panel reachability on BOTH layers — the
               curated-to-M2 crosswalk (which path is REQUESTED) plus the `--ld-file`
               thread (which path is OPENED; `{input.ld_matrix}` was a DAG declaration only
               and `run_susie_rss.R` rebuilt its own `AFR/` path, falling to identity);
               de-staled ingest/convert rules (AFR-only, `__sub` region ids,
               `build_ld_rds_aou_eur` retired); egress request planner on the EXISTING
               `ld_egress_bundle.plan_egress_bundles`; recorded egress-unit and Check-2
               redefinitions; then the terminal Carter gate for the in-perimeter fire.
       * ADD to the m3-05 entry (line 212): **SUPERSEDED-PENDING-REPLAN (2026-08-03)** — it
         inherits the same stale basis (322-row SHA-256 monolith, 44 sub-manifests,
         `EUR_aou` `.rds`, "Path A.1/A.2/A.3 region count"). Replan AFTER the panel lands,
         when the real banked-region count and the real bundle count are observable rather
         than assumed.
       * Update the phase `**Plans**:` count line (200) to include m3-04b and m3-04c.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3 -q &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile --list &gt; /dev/null &amp;&amp; test ! -e src/python/validate_bundle_sizes.py &amp;&amp; grep -q "Aggregate summary statistic" .planning/amendments/aou-egress-audit-log.md &amp;&amp; test "$(git diff 676fe77 -- .planning/amendments/aou-egress-audit-log.md | grep -c '^-[^-]')" -eq 0 &amp;&amp; grep -c "plan_egress_bundles" src/python/plan_ld_egress.py &gt; /dev/null &amp;&amp; grep -q "SUPERSEDED-PENDING-REPLAN" .planning/ROADMAP.md</automated>
  </verify>
  <acceptance_criteria>
    - Every one of the 276 unique `region_id` values in `config/ld_regions.tsv` matches the
      `region_id` wildcard pattern in BOTH `m3_ingest_aou_ld.smk` and
      `m3_convert_npz_rds.smk` (today 123 of them do not).
    - `grep -c "AFR|EUR" src/snakemake/rules/m3_ingest_aou_ld.smk` is 0.
    - `grep -c "rule build_ld_rds_aou_eur" src/snakemake/rules/m3_convert_npz_rds.smk` is 0,
      and `grep -c "EUR_ukbb_pub" src/snakemake/rules/m3_convert_npz_rds.smk` is at least 1.
    - `grep -ci "blockmatrix" src/snakemake/rules/m3_ingest_aou_ld.smk` is 0.
    - `test ! -e src/python/validate_bundle_sizes.py` exits 0.
    - `grep -c "plan_egress_bundles" src/python/plan_ld_egress.py` is at least 1.
    - `.planning/amendments/m3-egress-and-validation-protocol-addendum.md` exists, is at
      least 90 lines, and contains `2a`, `2b`, `2c`, `CONSERVATIVE PROJECT WORKING CEILING`,
      and `OSF amendment-update`.
    - `.planning/amendments/aou-egress-audit-log.md` keeps its 2026-04-28 ruling byte-intact:
      `grep -q "Aggregate summary statistic"` succeeds AND `git diff 676fe77` on that file
      shows **zero removed lines**.
    - `grep -c "m3-04b\|m3-04c" .planning/ROADMAP.md` is at least 2, and the m3-05 entry
      contains `SUPERSEDED-PENDING-REPLAN`.
    - `tests/m3` reports 0 failed, >= 496 passed, skips <= 31.
    - `snakemake --snakefile Snakefile --list` exits 0.
      ⛔ `snakemake --dry-run` is NOT a criterion here either (MEDIUM-7 / D-04b-03). It is
      unsatisfiable pre-fire in BOTH tasks, and this plan does not discharge it.
  </acceptance_criteria>
  <done>
    The consume path matches the real producer: AFR-only, 276 regions, subregion-split ids
    admitted, no retired `EUR_aou` rule, no reimplemented bundle sizer. The two protocol
    items that could not survive the m3-02e re-architecture are redefined in writing with
    their evidence, and the pre-registration consequence is routed to Carter rather than
    absorbed silently. The ROADMAP no longer advertises a plan that was never executed.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 3: The in-perimeter arc — PRE-FIRE fixes, the allow_degraded decision, the region-1 gate, the ~11-day billed fire, and egress</name>
  <files>none (Carter action; the agent verifies afterwards)</files>
  <action>See the human_gate block. No agent action. The agent's role is to verify the
  acceptance criteria after Carter completes the gate, and to re-run the m3-04b catalog rule
  once the real artifacts land.</action>
  <human_gate>
    <gate>AoU perimeter: PRE-FIRE fixes, the allow_degraded decision, region-1 validation, the 276-region native-plink LD fire, and egress</gate>
    <description>
      Every step below needs the AoU VPC-SC perimeter, which is NOT reachable from the NC
      State node (the `wb` control plane works; `gsutil` / `gcloud` / `bq` are walled). All
      of it is Carter's trigger. The AoU VM is STOPPED-not-deleted and holds the
      `/home/jupyter/afr_cohort` bfile; `.npz` is 0/276; nothing is running; $0.
      Read `.claude/skills/aou-ld-pipeline/SKILL.md` before any perimeter contact.

      ⛔ **GATE PRECONDITION — do not fire until Tasks 1a, 1b, 1c and 2 have merged.** Before them,
      the fire produces a panel the fine-mapping DAG cannot read
      (`DEC-2026-08-05-m3-ld-read-path`). That is the exact outcome the m3-04 replan existed
      to prevent.

      PRE-FIRE 1 — THE MANIFEST HAS NO PATH OUT OF THE PERIMETER (HIGH; decide before firing).
        `run_native_ld_panel.py:822` writes `{compute_dir}/occlusion_manifest.tsv`; in gs://
        mode `compute_dir` is LOCAL SCRATCH (:733); the upload set at :922-938 is ONLY
        `.npz`, `.afreq` and `.occluded.excludelist`. The manifest is never uploaded and dies
        with the scratch / VM. `_reclaim_region_scratch` globs `{region_id}.*`, so it
        survives per-region reclaim but not the VM.

        WHY IT IS NOT CODE IN m3-04b OR m3-04c: it edits the fire driver Carter is about to
        run for ~11 days, at exactly the moment the standing discipline says freeze-and-gate,
        and its only real verification is the fire itself. It belongs with the other PRE-FIRE
        items under the same review, not buried in a plumbing plan.

        WHAT IS AND IS NOT LOST WITHOUT IT: the LOCKSTEP still works. Production varids are
        `chr:pos:ref:alt` on GRCh38 (`run_native_ld_panel.py:391-400`), so `chr` and
        `pos_grch38` are recoverable from the excludelists, which ARE uploaded — that is what
        m3-04b's degraded reconstruction path is for. What is NOT recoverable is the occluder
        attribution, the REF spans, `occluding_deletion_ref_len`, and the reason / order
        labels — precisely the per-drop provenance the OSF amendment-update (osf.io/az52u,
        file `trsx5`) COMMITS TO PUBLISHING. This is a PRE-REGISTRATION compliance item, not
        a mechanics item.

        RECOMMENDATION: land it as its own reviewed `/gsd-quick` BEFORE the fire, uploading
        the manifest inside the existing `if ok:` block alongside the excludelist.
        RISK, STATED HONESTLY: `occlusion_manifest.tsv` is ONE file appended to by EVERY
        region. A bare `_gsutil_upload` overwrite races nothing on a single serial VM but
        would race under any future sharded fan-out, and the P3 lesson (`ff8cc47`) is that
        one upload helper serving two callers with opposite failure-safety needs silently
        destroyed banked provenance. LOWER-RISK OPTION, preferred: upload a PER-REGION
        `{region_id}.occlusion_manifest.tsv` so no object is ever overwritten —
        `aggregate_manifests` already expects a LIST of per-region manifests, and m3-04b's
        catalog rule already globs them.

      PRE-FIRE 1b — ⚠ **THE `allow_degraded` DEAD-END. Decide and RECORD it here, in
      writing, before firing** (HIGH-1; the old version of this gate left it implicit).
        ⚠ RE-ANCHORED 2026-08-05: `assemble_occlusion_catalog.py:368-380` is DOCSTRING
        PROSE, not the raise. There are now **TWO INDEPENDENT REFUSAL GATES**, and `fac9a93`
        (this session's BLOCKER-4 fix) added the first of them:

          GATE 1 — `:415-431`, `allow_partial_manifest` (default False).
            RAISES when the Stage-A rollup is NON-EMPTY but some regions have an
            excludelist and NO manifest ("REFUSING to stamp provenance_source=
            'stage_a_manifest' on a PARTIAL Stage-A rollup").
          GATE 2 — `:460-473`, `allow_degraded` (default False; `config/pipeline.yaml:266`).
            RAISES when the Stage-A manifests are absent or empty entirely ("REFUSING to
            assemble a DEGRADED occlusion catalog"). Proven against the real assembler:
            1 excludelist / 0 manifests / `allow_degraded=False` -> `ValueError`.

        STEP E below says only "re-run the catalog rule", and NOTHING flips either flag. So
        the post-fire state can dead-end STEP E: catalog missing -> both filter rules
        blocked -> every AFR `run_finemap` blocked, discovered after ~$385-1,084 and ~11
        days.

        The fail-loud design of BOTH gates is CORRECT and must not be softened into a silent
        fallback. What is required is a RECORDED decision covering **THREE** reachable
        states, not two:
          (i)   PRE-FIRE 1 LANDS AND EVERY REGION BANKS A MANIFEST (preferred). Both flags
                stay `false`; the catalog is stamped `stage_a_manifest`; nothing else
                changes.
          (ii)  PRE-FIRE 1 LANDS BUT SOME REGIONS STILL LACK A MANIFEST. ⚠ This state is
                LIVE even under branch (i): `run_native_ld_panel.py:821-831` treats the
                per-region Stage-A append as BEST-EFFORT and continues on any exception
                WHILE STILL WRITING the excludelist. GATE 1 fires. The correct response is
                to supply the missing manifests if recoverable; only if not, set
                `allow_partial_manifest: true` explicitly and record which regions are
                knowingly omitted (reported as `n_regions_excludelist_only`).
          (iii) PRE-FIRE 1 IS DECLINED. GATE 2 fires. Set `allow_degraded: true` **in the
                same act**, with a dated note in the SUMMARY stating explicitly which
                pre-registered provenance (occluder attribution, REF spans,
                `occluding_deletion_ref_len`, reason/order labels) will NOT be published,
                and confirming that the drop-set itself is still correct.
        Write the chosen branch into the SUMMARY **before** STEP B, and re-read it at STEP E
        — branch (ii) can only be diagnosed after the fire, so the gate must be re-entered
        rather than assumed settled. Task 3's acceptance criteria admit
        `provenance_source == excludelist_degraded` ONLY under branch (iii); under (i)/(ii)
        it must be `stage_a_manifest`. Mixed is impossible by construction
        (`assemble_occlusion_catalog.py:202` assigns it as a scalar) and must never be
        silently accepted.

      PRE-FIRE 2 — ROTATE THE STALE gs:// PANEL TSV (zero risk, zero compute cost).
        `gsutil stat <panel-uri>`; if present, `gsutil cat <uri> | head -1` must show 9
        tab-separated columns (the m3-07b `n_dropped_occluded` column sits at
        `_PANEL_COLUMNS` index 7); otherwise `gsutil rm`.
        "0/276 banked" is measured in `.npz` and does NOT evidence the TSV's absence: the
        `.npz`, not the TSV, gates the resume skip, and the June/July fires appended
        `status=error` rows unconditionally at :808 on both 7-column and 8-column code.

      PRE-FIRE 3 — THE GATED REAL-.bim VALIDATION.
        Byte-check that the occlusion exclude list computed on the REAL cohort `.bim` is
        exactly the five expected region-1 ids at 1980475, 5733487, 5922718, 7492693,
        8375822.
        OPEN AND UNRESOLVED: the 0- vs 1-based index origin of
        `_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES`. Settle it against the real `.bim`
        before trusting the comparison; an off-by-one here would validate the wrong rows.

      STEP A — REGION-1 RE-RUN GATE.
        Re-run region 1 ONLY. PASS = `.npz` count 0 -> 1, panel `status == ok`, `n_var`
        slightly under 102,421, `n_dropped_occluded` around 5 logged, no "not symmetric",
        no "Killed", no dmesg OOM. FAIL -> stop and report; do not proceed to 276.

        ⚠ **ALSO CHECK, at this gate, the SH2B3 coverage risk (MEDIUM-6).** The crosswalk
        maps `SH2B3_12q24` to `m2_region_00040__sub14` (RE-DERIVED 2026-08-05; the earlier
        `__sub00` was 66 Mb off target — see the `<interfaces>` oracle block). `__sub14`'s
        WINDOW fully contains the curated interval, and its CORE owns 523,169 of the
        600,000 bp (87.2%); the remaining 12.8% lies in `__sub15`'s core and is covered only
        through `__sub14`'s buffer. So the bp arithmetic is comfortable — but
        `run_susie_rss.R:184` gates on VARIANT `overlap >= MIN_LD_OVERLAP && coverage >=
        MIN_LD_COVERAGE` (50 and 0.5 per `config/susie_policy.yaml`), which is a realized
        variant-membership property, NOT a bp property. If the realized coverage falls short
        the panel is REJECTED and the fit falls to identity **with only a `message()`** — no
        artifact, no non-zero exit. Once `m2_region_00040__sub14` is banked, run one
        `run_finemap` for an AFR trait at
        `SH2B3_12q24` and read the estimate_s log line Task 1b extended: it now prints
        `ld_matrix` (the path OPENED) and `ld_file_declared` (the path DECLARED). If
        `ld_matrix` reads `identity`, the coverage gate rejected the panel — report it with
        the observed `ld_overlap` / `ld_overlap_fraction`, do not paper over it. The honest
        remedies are selecting `__sub15` instead (it also fully contains the locus), using
        the STITCHED parent `m2_region_00040` if one is built, or lowering
        `min_ld_coverage`. All three are scientific calls, not executor calls.

      STEP B — THE FIRE (~263 VM-h, ~11 days, ~$385-1,084).
        `nohup` plus `timeout 312h`, server-side, on the STOPPED-not-deleted Cloud Analysis
        VM. LIVENESS IS THE GCS `.npz` OBJECT LISTING CLIMBING TO 276 — not the kernel light,
        not a `_SUCCESS` marker, not the log. Do NOT restart the kernel. Check in every 2-3
        days. Teardown is UI-only (the in-perimeter pet SA has list-only Dataproc
        permissions), so there is no self-delete; the `timeout` wall-cap is the backstop.

      STEP C — SIZE AND PLAN THE EGRESS.
        `gsutil ls -l` over `ld/AFR_aou/*.npz` -> a `region_id, chr, bytes` TSV ->
        `python src/python/plan_ld_egress.py` -> `.planning/amendments/m3_egress_plan_AFR.tsv`.
        Expect at most 22 chromosome groups plus size splits. Confirm the REAL AoU egress
        threshold on the FIRST request: 50 GB is our working ceiling, not AoU's documented
        cap.

      STEP D — EGRESS TO NC STATE, PER GROUP.
        File the AoU egress request per group; `gsutil -m cp` the group's object URIs into
        `data/interim/aou_ld_exports/AFR_aou/`; ALSO fetch the `.occluded.excludelist` files,
        the `.afreq` sidecars, the panel TSV, and — if PRE-FIRE 1 landed — the occlusion
        manifest(s). Append one row per group to
        `.planning/amendments/aou-egress-audit-log.md` under `## Per-Bundle Audit Entries`
        with the Q12 schema, plus a per-group SHA-256 sub-manifest under
        `.planning/amendments/sha256/`. Commit per group with token `(m3-04c-T3-chr{N}-AFR)`.

      STEP E — HAND BACK TO THE DAG.
        Re-run m3-04b's catalog rule **under the branch recorded in PRE-FIRE 1b**: it now
        assembles the REAL catalog and the lockstep filter stops being a no-op. Then run the
        per-chromosome ingest flags and the `.npz` -> `.rds` conversion.

      STEP F — OSF AMENDMENT-UPDATE FOR THE CHECK-2 REDEFINITION.
        `.planning/amendments/m3-egress-and-validation-protocol-addendum.md` redefines a
        PRE-REGISTERED hard gate (AOU-LD-PIPELINE.md §9). Agent DRAFTS, Carter POSTS to
        osf.io/az52u, and the file GUID is recorded in-repo — the m3-07a discipline. No
        redefined check may be cited as PASSED before that posting is recorded.

      STEP G — THE END-TO-END READ-PATH PROOF ON REAL DATA.
        The whole point of Tasks 1a+1b together. After the `.rds` land, run one AFR `run_finemap` for a
        curated region with an M2 counterpart and confirm from its output JSON that
        `ld_file_declared` and `ld_matrix` are the SAME `AFR_aou/...rds` path, and that
        `ld_matrix` is neither `identity` nor an `AFR/` path. That is `resolved ==
        what-the-script-opens`, observed on production data rather than on a fixture.
    </description>
    <unblocks>the m3-05 replan (closeout + OSF), the M2-supplementary phase (slug m2-supp-aou-afr-rerun), and M4 genome-wide fine-mapping</unblocks>
    <how-to-resolve>
      1. Confirm Tasks 1a, 1b, 1c and 2 have merged. Do not fire before that.
      2. Decide PRE-FIRE 1: land the manifest upload as a reviewed quick task (per-region
         file preferred), or accept the degraded excludelist reconstruction.
      3. Decide and RECORD PRE-FIRE 1b (`allow_degraded`) in the SUMMARY, in the same act as
         step 2. Branch (i) or branch (ii) — never leave it implicit.
      4. Run PRE-FIRE 2 and PRE-FIRE 3.
      5. Fire the region-1 gate, including the SH2B3 coverage check; proceed only on PASS.
      6. Fire the 276-region loop; check in every 2-3 days against the GCS `.npz` count.
      7. Plan and file the egress; land the objects on GPFS; commit the audit rows.
      8. Re-run the catalog rule and the conversion rules; then STEP G.
      9. Type "approved" when all of it is complete, or describe exactly where it stopped.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; NPZ=$(ls data/interim/aou_ld_exports/AFR_aou/*.npz 2&gt;/dev/null | wc -l) &amp;&amp; RDS=$(ls data/processed/ld_reference/AFR_aou/*.rds 2&gt;/dev/null | wc -l) &amp;&amp; CAT=$(tail -n +2 data/processed/occlusion/occlusion_catalog_m3.tsv 2&gt;/dev/null | wc -l) &amp;&amp; echo "npz=$NPZ rds=$RDS catalog_rows=$CAT of 276 planned" &amp;&amp; test "$NPZ" -gt 0 &amp;&amp; test "$RDS" -eq "$NPZ" &amp;&amp; test "$CAT" -gt 0 &amp;&amp; grep -q 'Aggregate summary statistic' .planning/amendments/aou-egress-audit-log.md &amp;&amp; grep -rl 'AFR_aou' results/finemap 2&gt;/dev/null | head -1 &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3 -q</automated>
  </verify>
  <acceptance_criteria>
    - `ls data/interim/aou_ld_exports/AFR_aou/*.npz | wc -l` equals the number of regions the
      fire actually banked, and that number is recorded in the SUMMARY against the 276
      planned. Do NOT hardcode 276 as a pass bar before the fire has run: a partial bank is a
      real, reportable outcome, not a failure to be papered over.
    - `ls data/processed/ld_reference/AFR_aou/*.rds | wc -l` equals the banked `.npz` count.
    - `data/processed/occlusion/occlusion_catalog_m3.tsv` has more than 0 data rows, and its
      `provenance_source` column matches the branch RECORDED in PRE-FIRE 1b:
      `stage_a_manifest` under branch (i), `excludelist_degraded` under branch (ii) with
      `allow_degraded: true` visible in `config/pipeline.yaml`. Never absent, never a value
      that contradicts the recorded branch.
    - **THE READ-PATH PROOF (STEP G).** At least one AFR `run_finemap` output JSON for a
      curated region with an M2 counterpart has `ld_file_declared == ld_matrix`, both
      pointing at a `data/processed/ld_reference/AFR_aou/m2_region_*.rds` path.
      `ld_matrix` must NOT be `identity`, `identity_fallback`, or any `.../AFR/...rds` path.
      This is the production-data form of the DEC-2026-08-05 acceptance test.
    - The SH2B3 coverage check (MEDIUM-6) is recorded with its result: either the
      `m2_region_00040__sub00` panel was ACCEPTED at `SH2B3_12q24`, or it was rejected on
      coverage and the rejection is reported with the observed `ld_overlap` /
      `ld_overlap_fraction` — not silently absorbed as an identity fit.
    - At least one `(m3-04c-T3-chr` commit token per egress group appears in the git log,
      with a matching SHA-256 sub-manifest under `.planning/amendments/sha256/`.
    - `.planning/amendments/aou-egress-audit-log.md` still contains its 2026-04-28 ruling
      text byte-intact.
    - The occlusion catalog's row count and the panel TSV's summed `n_dropped_occluded` agree,
      making "the panel and the sumstats dropped the same variants" a checked claim.
    - `pytest tests/m3` still shows 0 failed after the real artifacts land.
  </acceptance_criteria>
  <done>
    The AFR LD panel exists on GPFS, the fine-mapping DAG provably READS it (declared path ==
    opened path, observed on production output, not on a fixture), its occlusion provenance
    crossed the egress boundary in a recorded form (full or explicitly degraded, per a
    decision taken BEFORE the money was spent), the lockstep filter is live rather than a
    no-op, and the audit log carries one row per egress group. m3-05 can be replanned against
    observed numbers instead of assumed ones.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Snakemake's DAG declaration vs the R script's read path | The boundary BLOCKER-1 lives on. A declared `input:` absent from the rule's `shell:` is a DAG declaration ONLY; the consumer rebuilds its own path and can silently open something else, or nothing. This plan closes it by making the declared artifact the argument the script opens. |
| AoU bucket to NCSU GPFS | The production egress crossing. Only aggregate summary artifacts cross: per-region `.npz` LD, `.afreq`, `.occluded.excludelist`, the panel TSV, and (if PRE-FIRE 1 lands) the occlusion manifest. No `.bed` / `.bim` / `.fam` ever leaves the compute node (REQ-AOU-LD-EGRESS). |
| Curated Track-A region namespace vs the M2 276-region namespace | The crosswalk is the ONLY place the two naming conventions meet. A wrong row silently points a fine-map at another locus's LD matrix. |
| Pre-registered protocol (OSF `az52u`) vs what is executable | Two §9 / §7 items cannot be run as written. Redefining them in-repo without an OSF amendment-update would be an undisclosed pre-registration deviation. |
| The test suite vs the change it is supposed to guard | Two tests assert the exact pre-change strings this plan must replace. A suite that forbids its own successor's change is a boundary: the escape hatch is an executor weakening the wrong assertion. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-m3-04c-01 | Tampering | curated-to-M2 crosswalk | mitigate | ⚠ REALIZED ONCE ALREADY. Selection now happens on LIFTED GRCh38 windows in a single coordinate build, never on the parent-repeated `start/end_grch37` columns that silently tied 18 ways and put the anchor locus 66 Mb off target. Containment beats overlap; `partial` is never promoted to `contained`; unmapped resolves to the byte-identical legacy value. Validated by PHYSICAL GEOMETRY (T1.5) rather than by re-running the ranking, with a named regression pin that `__sub00` is not selected (T1.6) — because the prior "independent 12/12 reproduction" re-implemented the same rule and reproduced the bug. Chromosome comparison strips a `chr` prefix on both sides. |
| T-m3-04c-15 | Tampering | a test assertion that cannot fail | mitigate | The STEP 7 regex broadening would have made the `region_id` kwarg assertion VACUOUS (the module docstring's `resolve_ld_path()` mentions let a non-greedy scan match `params.region_id` 30+ lines away). Replaced with a balanced-paren call-site extractor, plus a PERMANENT negative-control test (`test_kwarg_assertion_is_not_vacuous`) that sabotages the real call site in memory and asserts the check still fails. Validated on four inputs during planning. |
| T-m3-04c-16 | Denial of service | the SECOND catalog refusal gate | mitigate | `fac9a93` added `allow_partial_manifest` (`:415-431`) alongside `allow_degraded` (`:460-473`). A per-region Stage-A append failure is swallowed by `run_native_ld_panel.py:821-831` WHILE the excludelist is still written, so GATE 1 can fire even when PRE-FIRE 1 lands. PRE-FIRE 1b now models THREE states and requires the gate to be RE-ENTERED at STEP E, because branch (ii) is only diagnosable after the fire. |
| T-m3-04c-02 | Spoofing | the LD artifact actually opened | mitigate | The declared `{input.ld_matrix}` is passed as `--ld-file` and placed FIRST in the loader's candidate list, so the resolver is the single source of truth. Proven BEHAVIOURALLY (T2.3-T2.6) against the real R loader, with an `AFR_aou` path the `ld_dir` reconstruction can never reach — not by a green DAG. Every output JSON records `ld_file_declared` beside `ld_matrix`, so the identity holds as a per-region receipt after the fire (STEP G). |
| T-m3-04c-03 | Tampering | the test suite as the guard | mitigate | The two failing assertions are rewritten in NAMED, reviewed steps with verbatim before/after text, both STRICTLY STRONGER; the `params.region_id` guard rail one line above is preserved character-for-character; and the plan carries an explicit STOP instruction for any OTHER failing test. Precedent for replace-don't-relax: `1a9d170`, m3-04b's `test_production_boundary_documented`. |
| T-m3-04c-04 | Repudiation | occlusion manifest never leaving the perimeter | mitigate + transfer | m3-04b's degraded reconstruction makes the loss VISIBLE in the artifact (`provenance_source=excludelist_degraded`) rather than inferable from absence. The producer-side fix is escalated to Carter as PRE-FIRE 1, and the `allow_degraded` consequence is now a RECORDED pre-fire decision (PRE-FIRE 1b) rather than a post-spend discovery. |
| T-m3-04c-05 | Denial of service | the `allow_degraded` dead-end | mitigate | HIGH-1. The assembler's refusal is CORRECT and stays loud; the gate now forces the branch to be chosen and written down BEFORE STEP B, and the acceptance criteria bind `provenance_source` to the recorded branch instead of accepting either value. |
| T-m3-04c-06 | Repudiation | the silent Path-2 revert | mitigate | HIGH-2. Path 2 now sets `variant_catalog_fallback` (parity with Path 1) plus a NEW `ld_overlap_zero_fallback` that distinguishes the two, and both are READ by the per-region estimate_s log, so the flags stop being write-only. Science behaviour unchanged: still one retry against `subset_base`. |
| T-m3-04c-07 | Information disclosure | egress request grouping | mitigate | Grouping is REQUEST-LEVEL over already-egress-clean aggregate objects; `plan_egress_bundles` never touches genotypes. Every group gets an audit-log row (AoU request id, size, region ids, SHA-256 sub-manifest) under the 2026-04-28 HARD GATE classification. |
| T-m3-04c-08 | Tampering | the append-only audit log | mitigate | The scope correction is APPENDED; the 2026-04-28 ruling text stays byte-intact, enforced by a zero-removed-lines `git diff` check plus a grep for `Aggregate summary statistic`. |
| T-m3-04c-09 | Repudiation | Check-2 redefinition without disclosure | mitigate | The redefinition is written to a dated in-repo addendum with its evidence, and STEP F routes an OSF amendment-update through Carter before any redefined check may be cited as passed. Mirrors the m3-07a gate discipline. |
| T-m3-04c-10 | Denial of service | an ~11-day unattended billed fire | mitigate | `timeout 312h` hard wall-cap; 2-3 day check-in cadence; liveness measured as the GCS `.npz` listing, not the kernel light; resume-safe skip guard keyed on the banked `.npz`. Plus a merge precondition: the fire cannot start before the read path is closed. |
| T-m3-04c-11 | Tampering | silent numerics change on curated AFR regions | mitigate | Task 1c step 4 records that the first curated AFR region with an `AFR_aou/.rds` switches panels and its fine-mapping numerics WILL change, and names `ld_panel.pin.AFR` as the hold switch. Disclosed, not absorbed. |
| T-m3-04c-12 | Tampering | an unsatisfiable acceptance criterion inviting a fake artifact | mitigate | MEDIUM-7. `snakemake --dry-run` is STRUCK from both tasks and replaced with `--list`, with an explicit "if you feel the urge to touch a fake `.rds`, STOP" instruction. Re-proved firsthand that `resolve_ld_path` raises for BOTH the pre- and post-crosswalk id. |
| T-m3-04c-13 | Tampering | SH2B3 sub-window rejected on coverage, falling to identity | mitigate | MEDIUM-6. `__sub14`'s window fully contains the locus and its core owns 87.2% of it, but `run_susie_rss.R:184` gates on realized VARIANT overlap/coverage, not bp. Checked explicitly at the region-1 gate using the newly-logged `ld_matrix` value, with three named remedies (`__sub15`, the stitched parent, or `min_ld_coverage`) all flagged as scientific calls. The 12.8% core straddle is DISCLOSED in `finemap.smk` and the SUMMARY rather than absorbed. |
| T-m3-04c-14 | Information disclosure | `.npz` triangle-flag disagreement | accept (already mitigated upstream) | `plink_ld_to_npz.py` writes `lower_triangular` and `ld_npz_to_rds.R` honours it; both are FROZEN here (0-line diff gated). No new `.npz` producer or consumer is introduced by this plan. |
</threat_model>

<verification>
Plan-level checks. Items 1-9 are NC-State, $0, no perimeter; items 10-12 apply only after
the Task 3 gate.

1. `pytest tests/m3 -q` reports **0 failed, >= 496 passed, <= 31 skipped**
   (baseline at `676fe77`: 527 collected / 496P / 31S / 0F).
2. The four BEHAVIOURAL read-path tests RAN (did not skip).
3. `git diff --exit-code 676fe77 --` is clean for `plink_ld_to_npz.py`, `ld_npz_to_rds.R`,
   `condition_ld_matrix.py`, and the four m3-07 modules.
4. `snakemake --snakefile Snakefile --list` exits 0.
   ⛔ `snakemake --dry-run` is deliberately NOT a check (MEDIUM-7 / D-04b-03).
5. `finemap.smk` contains `--ld-file {input.ld_matrix}` exactly once, and
   `region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],` exactly once.
6. `finemap.smk` still does NOT contain `SUPERSEDED-PENDING-REPLAN`, and still contains
   `m3-04b`, `m3-04c`, `occlusion_lockstep` and `consume`
   (`test_finemap_loader_contract.py:152-165`).
7. Every one of the 276 unique `region_id` values in `config/ld_regions.tsv` matches the
   `region_id` wildcard in both M3 rule files.
8. `test ! -e src/python/validate_bundle_sizes.py` exits 0 (the helper already shipped).
9. `git diff 676fe77 -- .planning/amendments/aou-egress-audit-log.md` shows zero removed lines.
10. Banked `.npz` count equals the `.rds` count, and both are recorded against 276 planned.
11. At least one production `run_finemap` JSON shows `ld_file_declared == ld_matrix`, both an
    `AFR_aou/m2_region_*.rds` path, neither `identity` nor `AFR/`.
12. The occlusion catalog row count agrees with the panel TSV's summed `n_dropped_occluded`,
    and `provenance_source` matches the PRE-FIRE 1b branch recorded before the fire.
</verification>

<success_criteria>
- The AoU AFR panel is REACHABLE on BOTH layers: a curated region with an M2 counterpart
  resolves to `AFR_aou/m2_region_NNNNN.rds`, AND `run_susie_rss.R` opens that exact file.
  An unmapped region resolves to the byte-identical legacy value and the `--ld-dir`
  reconstruction still works for every caller that does not pass `--ld-file`.
- `resolved == what-the-script-opens` is demonstrated behaviourally against the real R
  loader before the fire, and again on production output after it. A green DAG was never
  accepted as evidence.
- The two tests that contradicted this plan are stronger than they were, and the
  `params.region_id` guard rail survived character-for-character.
- The `ld_overlap == 0` revert is no longer invisible, and something actually reads the flag.
- The ingest and convert rules describe the producer that exists: AFR-only, 276 regions,
  subregion-split ids admitted, `build_ld_rds_aou_eur` retired.
- The egress plan is produced by the shipped `plan_egress_bundles`; no duplicate sizer exists.
- Both unrunnable protocol items are redefined in a dated, evidenced, in-repo addendum, and
  the OSF amendment-update is routed to Carter rather than skipped.
- The `allow_degraded` branch is chosen and recorded BEFORE ~$385-1,084 is spent, not
  discovered after.
- The ROADMAP no longer advertises a never-executed plan, and m3-05 is marked for replan.
- The in-perimeter arc is fully enumerated with its PRE-FIRE decisions, its liveness signal,
  its SH2B3 coverage check and its honest risk statement, and is gated on Carter.
</success_criteria>

<output>
After completion, create
`.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-W4-panel-reachability-egress-and-fire-SUMMARY.md`
recording:
- The full 12-row crosswalk with each region's `status`, and which curated regions are now
  eligible to switch from `AFR_1kg` to `AFR_aou` (the disclosable numerics change).
- **The read-path evidence**: the behavioural test output showing the real loader opening
  the declared `AFR_aou` artifact, and (post-fire) the production JSON showing
  `ld_file_declared == ld_matrix`. State plainly that a green DAG was not accepted as proof.
- The exact before/after text of the two rewritten assertions, and confirmation that no
  other pre-existing test was edited.
- The PRE-FIRE 1 decision actually taken (manifest upload landed, or degraded reconstruction
  accepted) and, if degraded, an explicit statement of the pre-registered provenance not
  published.
- **The PRE-FIRE 1b `allow_degraded` branch**, recorded with its date and its consequence.
- The region-1 gate result INCLUDING the SH2B3 coverage check, the fire's wall clock and
  dollar cost against the ~263 VM-h / ~$385-1,084 estimate, and the banked region count
  against 276.
- The realised egress group count and per-group sizes against the at-most-22 projection,
  plus the REAL AoU egress threshold learned on the first request (vs our 50 GB working
  ceiling).
- Any region failures with their `status` strings from the panel TSV.
- The OSF amendment-update posting state for the Check-2 redefinition (GUID once posted).
- What m3-05 must now be replanned against: the observed banked-region count, the observed
  egress group count, AFR-only artifacts, and no `EUR_aou` `.rds`.
</output>
