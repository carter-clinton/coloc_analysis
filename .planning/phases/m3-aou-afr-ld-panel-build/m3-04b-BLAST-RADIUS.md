# m3-04b BLAST RADIUS — post-landing downstream assessment

**Date:** 2026-08-04
**Assessed at:** HEAD `2bda675` (m3-04b landed: `d7dfa67`, `0cae502`, `37c51df`, `f038ce0`)
**Method:** four independent read-only investigators across orthogonal downstream
dimensions, plus orchestrator-side verification of every load-bearing claim.
**Cost:** `$0`, NC State only, no perimeter contact, no repo mutation during the sweep.

---

## ★ HEADLINE — the fire is still blocked, and m3-04c Task 1 as written does NOT unblock it

The 2026-08-03 handoff correctly said *do not fire: the `AFR_aou` panel is unreachable
from `run_finemap`*, and correctly identified the missing curated→M2 crosswalk. That
diagnosis is **right but one layer too shallow**.

`run_finemap` **declares** its LD panel through `resolve_ld_path` on `input.ld_matrix`,
but **`{input.ld_matrix}` is never referenced in the rule's shell block**. The R script
receives only `--ld-dir {params.ld_dir}` and `--region {params.region_id}`, and
reconstructs its own path:

```r
# src/legacy/region_analysis/scripts/run_susie_rss.R:124-127
candidates <- unique(c(
  file.path(ld_dir, ancestry, paste0(region_id, ".rds")),
  file.path(ld_dir, ancestry, paste0(safe_id,   ".rds"))
))
```

`ancestry` is `AFR` — never `AFR_aou`. **No rule promotes `AFR_aou/*.rds` into `AFR/`**
(grep over every `.smk` and the Snakefile: zero hits). So the AoU panel directory is not
in the candidate set at all, and on a miss the script falls **silently to an identity
matrix** (`run_susie_rss.R:472-474`, `R <- diag(nrow(subset))`).

### Proven empirically, not argued

Simulating the post-fire world (AoU panel present on disk, crosswalk applied):

| | path |
|---|---|
| DAG declares (`input.ld_matrix`) | `…/ld_reference/AFR_aou/m2_region_00067.rds` — **exists** |
| SuSiE actually opens | `…/ld_reference/AFR/FTO_16q12.rds` — **absent** |
| same file? | **No** |

**Consequence:** after m3-04c Task 1 lands and the fire banks 276 `.npz`, Snakemake would
*require* the AoU `.rds` to exist before running, and SuSiE would still fine-map on an
identity matrix. The ~11-day, ~$385–1,084 fire would **still** produce a panel nothing
reads. m3-04c's `must_haves.truths[0]` ("The `AFR_aou` panel is REACHABLE from
`run_finemap`") is **false as specified**, and Task 1's `<done>` claim is unearnable.

**Attribution, stated honestly.** This defect is **PRE-EXISTING** — introduced by m3-W3-T2,
which wired `resolve_ld_path` into `input:` only. m3-04b did not cause it. m3-04b
*reinforced the belief* in it: the new module docstring (`finemap.smk:8-19`) says
`input.ld_matrix` "is now routed through `resolve_ld_path()`", and the new comment block
hands "panel reachability" to m3-04c as though the one-argument swap discharges it.
Confirmed independently by three separate investigators and by direct orchestrator
verification.

**Fix requires a THIRD change m3-04c does not contain** — one of: thread `{input.ld_matrix}`
into `run_susie_rss.R` behind a new `--ld-file` argument; add a promote/symlink rule from
`AFR_aou/` into the read path; or make `ld_dir` per-ancestry-source. All three touch a
frozen-adjacent R script. **This is a scope decision for Carter, not an executor's call.**

### And a second, independent blocker on the same fire

**BLOCKER-4** (below) is unrelated to reachability and equally disqualifying for the fire's
*output*: if even one region's Stage-A manifest write fails — a path
`run_native_ld_panel.py:821-831` explicitly swallows — the catalog assembler **ignores every
excludelist**, silently omits those regions, and stamps the result `stage_a_manifest`. The
occluded variants of the omitted regions are then never dropped from the sumstats. That is
the orphaned-variant failure the pre-registration exists to forbid, wearing a
provenance stamp that says everything is fine. Unlike BLOCKER-1, **this one is autonomous,
`$0`, and should be fixed before the fire rather than decided.**

---

## 1. Verified safe — what the sweep cleared, and why

Each item below is cleared for a *stated reason*; re-check the reason, not the sweep.

**The non-AFR byte-identity claim is empirically true.** Across every `(trait, ancestry)`
and `(region, ancestry)` combination the pipeline instantiates, and across all 10
schema-passing config permutations, EUR/TRANS/EAS/HIS/SAS sumstats and variants paths
come back character-for-character identical to the pre-m3-04b expressions. Two independent
barriers enforce it: the ancestry gate in `occlusion_lockstep_cli.py:104-127`, and a
`stem=r"[A-Za-z0-9_.\-]+\.AFR"` wildcard constraint (`m3_occlusion_lockstep.smk:284`) that
Snakemake itself confirms EUR cannot cross (`MissingRuleException` on a EUR mirror target).
**Track-A and EUR numerics cannot move through this change.**

**Both `run_finemap` inputs move together — there is no half-wired job.** Empirically over
the real 178-job DAG: `run_finemap` shows 36 jobs filtered on *both* axes (12 regions × 3
AFR traits) and 60 unfiltered on *both*. No job got one input moved and not the other.

**The change is strictly additive.** Kill-switch A/B on the same tree: `enabled: true` → 178
jobs, `enabled: false` → 162. The delta is exactly the 16 new jobs. No other rule's job
count or input set changes.

**DAG integrity holds.** No cycles, no ambiguity, no wildcard collision. The mirror cannot
shadow or feed the original (sibling directories, no prefix relation). The four live config
overlays preserve the new block.

**Mirror format fidelity is complete.** Verbatim header, byte-identical survivor rows,
preserved input order and trailing newline, idempotent on its own output, and genuine BGZF
(FEXTRA set, `BC` subfield, EOF block) with a `tabix` invocation matching `sumstats.smk:157`
flag-for-flag.

**Alignment is by identifier, not position.** `run_susie_rss.R:78-121` matches `SNP_ID`
first, then a `CHR:POS` key, then *subsets* `R <- R[ld_idx, ld_idx]`. A membership
difference between panel and filtered sumstats is handled, not silently mis-ordered. **This
is what converts the F2 defect from a corruption into a detectable over-exclusion.**

**Key-space guards are present where it matters.** `_parse_excludelist_variant` returns
`None` on a malformed id and counts `n_unparseable` rather than coercing;
`_load_manifest_keys` fails **closed** when `pos_grch37` is absent. The region-id suffix
strip correctly admits `m2_region_00040__sub00`.

**Tests are genuine, not tautological.** 444 passed / 31 skipped / 0 failed, independently
re-run. `test_non_afr_input_paths_are_byte_identical` is parametrized over five ancestries
and builds its expectation from the same `os.path.join` form the legacy rule used, so it
would catch a merely-normalizing resolver. No mock-return assertions.

**`provenance_source` can never MIX within one catalog, and is never absent.**
`assemble_occlusion_catalog.py:202` assigns it as a scalar over the whole frame in all three
branches; verified uniform in the mixed, degraded and empty cases. (An undocumented third
value `"empty"` appears only in the returned dict, never on a row — cosmetic.)

**The degraded path loses attribution but NOT drop correctness**, and it is gated behind a
loud `ValueError` with `allow_degraded: false` in config. Verified 2/2 dropped from a
degraded catalog, with the four unrecoverable columns as explicit `pd.NA`. This is good
design — and it is *precisely because* the degraded path refuses loudly that the silent
partial-manifest path (BLOCKER-4) is the dangerous one.

**D-04b-02 (stale `.tbi`) has no exposure in the new code.** No m3-04b path performs a tabix
range query — all four modules use `gzip.open` streaming, and the only `tabix` call is index
*creation* run after the mirror write in the same shell, so the mirror's index is fresh by
construction. (`collect_region_variants_tabix.py` does use range queries, but
`ld_reference.smk:219` wires the **non-tabix** variant. Note `hdl.AFR`'s `.tbi` is 71 bytes —
an *empty* index, not merely stale.)

**The variant-list path is coordinate-safe.** `collect_region_variants.py:157` casts
`POS` with `.astype(int)` and writes a header, so `filter_variants` always sees integer
positions and locates columns by name.

**`asthma.AFR`'s 1,172 unplaced-contig rows produce no false drops** — `_canonical_key`
leaves them as strings, which never match a numeric manifest key.

**The pinned freeze is real.** All seven pinned files (four m3-07 modules + three frozen
contracts) verified 0-line diff vs `bf16289`, working tree clean.

**The m3-04c plan's factual basis is sound** (in contrast to m3-04b's, which was wrong
twice). Every interface claim verified: 12 curated rows, 276 mapping rows with zero curated
slugs, 552/276/123 in `ld_regions.tsv`, and all stale artifacts exactly where stated. The
plan's known-answer crosswalk oracle was **independently reimplemented and reproduced 12/12
exactly**, including `SH2B3_12q24 → m2_region_00040__sub00` selected from 18 containing
candidates (the tie-break is genuinely load-bearing) and `BMI_Xq24` as the sole unmapped
chrX region.

---

## 2. Newly introduced or aggravated — severity-ordered

### BLOCKER-1 (F2) — `input.ld_matrix` is a DAG declaration only
See headline. **PRE-EXISTING; belief aggravated by m3-04b.**
**Blocks: the ~11-day billed fire, and m3-04c's headline must_have.**

### BLOCKER-2 (F1) — m3-04b landed a test that hard-fails on the exact edit m3-04c must make
`tests/m3/test_occlusion_lockstep_wiring.py:410` asserts
`"region_id=REGION_SAFE_TO_ID[wildcards.region]," in src` — character-for-character the
string m3-04c Task 1 step 4 must replace. The test's **own docstring three lines above says
"m3-04c DOES change the sibling `resolve_ld_path(region_id=...)` argument."** It forbids
what it documents as m3-04c's job. Proven by simulation: applying the plan's edit verbatim
yields `1 failed, 13 passed`.

`:414`'s `assert src.count("REGION_SAFE_TO_ID") == 3` compounds it — a brittle whole-file
count that m3-04c's mandated comment rewrite also moves.

**The danger is the shape of the escape.** The real `params.region_id` pin sits at `:406`,
*immediately above* the failing assertion. An executor told "make `tests/m3` pass" is baited
straight at the one line the project has repeatedly ruled must never change. This is the
baked `feedback_check_plan_against_red_before_executing` pattern recurring.
**NEWLY-INTRODUCED. Blocks: the m3-04c merge.**

### BLOCKER-3 (F5) — every `finemap.smk` line number in the m3-04c plan is stale, and the do-not-touch guard now points at the wrong block
m3-04b added +48 lines above `params:`. The plan was verified at `9fe26f6` (pre-m3-04b).

| plan says | actually at `2bda675` |
|---|---|
| `:158  params.region_id … MUST STAY AS-IS` | `:206`; **`:158` is now a comment inside `input.ld_matrix`** |
| `read_first :155-169 (params — do not touch)` | now the **`ld_matrix` block m3-04c must rewrite** |
| `REPLACE the CR-001 comment at :117-123` | `:117-123` is **m3-04b's own comment**; CR-001 is at `:165-171` |
| `:124-131 ld_matrix=resolve_ld_path(...)` | `:172-179` |

An executor following step 4 literally would delete m3-04b's new comment and leave CR-001
intact, while the real `params.region_id` at `:206` sits unguarded in prose.
**NEWLY-INTRODUCED. Blocks: the m3-04c merge.**

### BLOCKER-4 — a PARTIAL Stage-A rollup silently discards every excludelist-only region and stamps the result `stage_a_manifest`

`assemble_occlusion_catalog.py:352-359`:

```python
if not rollup.empty:
    source = PROVENANCE_STAGE_A_MANIFEST
    if excludelist_paths:
        print("... the {N} excludelist(s) are IGNORED "
              "(the manifests carry strictly more provenance).")
    _write_stage_a(rollup.to_dict("records"), stage_a, source)
```

The override fires when the rollup is merely **non-empty** — not when it is **complete**.
The note's claim is true *per region* and **false as a set claim** when the manifest set is
a subset of the regions.

**The state that triggers it is live and already coded.** `run_native_ld_panel.py:821-831`
treats the per-region Stage-A append as best-effort: on any exception it prints
`WARN … the .occluded.excludelist still records the drop set` and continues — **while the
excludelist is still written**. Every region that trips it becomes excludelist-only. So does
every region built before a producer-side manifest-upload fix (PRE-FIRE 1).

**There is no completeness check anywhere.** `n_regions` is *computed* at `:424` and
*reported*, never compared against the 276 AFR regions in `config/ld_regions.tsv`.

Verified end-to-end with 1 Stage-A manifest + 1 excludelist-only region, both variants
genuinely present in the sumstats:

```
return : {'n_regions': 1, ..., 'source': 'stage_a_manifest'}
catalog: 1 row — region m2_region_00002 ABSENT
drop   : {'n_in': 3, 'n_dropped': 1, 'n_out': 2}    # truth: 2 rows should have gone
```

The result is **orphaned variants in the sumstats — precisely the failure the pre-registered
lockstep exists to prevent — wearing a `stage_a_manifest` provenance stamp.** Note the irony
that the *degraded* path is safe because it is gated behind a loud `ValueError`; it is the
**silent partial-manifest path** that is dangerous.

**NEWLY-INTRODUCED. Blocks: the first fire that banks Stage-A manifests.** Fix = a region
coverage assertion (`n_regions` vs the AFR region count), or make manifest+excludelist a
**union** rather than an override.

### HIGH-0 — the one guard that could have caught a parse failure is structurally incapable of firing

`enrich_occlusion_manifest`'s total-miss guard (`occlusion_manifest.py:385`) tests
`any(k in present_rate for k in keys_present)`, but the scan keys are built **from the
manifest's own lifted rows** (`assemble_occlusion_catalog.py:399-410`), and
`scan_present_rate` returns a record for **every requested key** (`n_traits_present: 0`,
`occlusion_present_rate_scan.py:185-192`). The membership test is therefore always True.
It detects key-*shape* drift and nothing else.

Verified: a manifest lifted to `(1, 5982778)` scanned against the float-POS file alone
publishes `n_traits_present=0, traits_present='[]'` and **does not raise**. If every AFR
file were float-formatted, the catalog would publish "present in 0 of 9 traits" for every
row — a wholly wrong pre-registered claim — with zero error signal. Today it publishes
**6/9 instead of the correct 7/9** for rs182965575.
**NEWLY-INTRODUCED** (the guard's inadequacy was unobservable at zero callers).

### HIGH-1 (F3) — declining PRE-FIRE 1 dead-ends STEP E *after* the money is spent
`config/pipeline.yaml:266` sets `allow_degraded: false`.
`assemble_occlusion_catalog.py:368-380` **raises** when excludelists are present but Stage-A
manifests are absent. The fire uploads `.occluded.excludelist` but **not** the manifest —
that is exactly PRE-FIRE 1. Proven against the real assembler: 1 excludelist / 0 manifests /
`allow_degraded=False` → `ValueError: REFUSING to assemble a DEGRADED occlusion catalog`.

Task 3 STEP E says only "re-run the catalog rule". Nothing flips `allow_degraded`. Yet Task
3's acceptance criteria explicitly admit `provenance_source == excludelist_degraded` as
valid — **unreachable without the flip**. So the plan's own "accept the degraded
reconstruction" branch dead-ends: catalog missing → both filter rules blocked → every AFR
`run_finemap` blocked, discovered after ~$385–1,084 and 11 days.

The fail-loud design is *correct*; the gate documentation is what is missing.
**NEWLY-INTRODUCED. Blocks: the fire's STEP E.**

### HIGH-2 (orchestrator) — TWO revert paths discard the lockstep, and the second is fully silent
`run_susie_rss.R` has two paths that throw away variant-catalog filtering:

- **Path 1** (`:342-355`) — AFR-only, fires on an empty filtered subset. Sets
  `used_variant_catalog <- FALSE` **and** `variant_catalog_fallback <- TRUE`. Observable.
- **Path 2** (`:423-428`) — **not ancestry-gated**, fires when `ld_overlap == 0`. Sets
  `used_variant_catalog <- FALSE` but **never sets `variant_catalog_fallback`**. It reverts
  to the unfiltered `subset_base` with **no distinguishing signal at all**.

And **no downstream consumer reads either flag** — both are written to JSON and never
checked (verified by grep across `.py`/`.R`/`.smk`).

If Path 2 fires post-fire, the occlusion lockstep is silently defeated for that region and
occluded variants re-enter the fine-map. m3-04b makes the AFR variant list newly
*shrinkable*; m3-04c will introduce a *new* LD source with different varid provenance.
Both raise the probability of `ld_overlap == 0`.
**PRE-EXISTING, AGGRAVATED. Blocks: the fire (and any claim the lockstep held).**

### HIGH-3 — the LD panel side of the lockstep is unfiltered and unaudited
`build_ld_rds` consumes the **unfiltered** variant list while `occlusion_filter_variants`
writes the filtered sibling. The `{n_in, n_dropped, n_out}` counts artifact covers the
sumstats and variant-list sides only. **There is no artifact making "the panel dropped the
same variants" checkable** — which is the exact claim the pre-registration rests on.
**NEWLY-INTRODUCED (the split). Blocks: the OSF provenance claim, not the merge.**

### HIGH-4 — no positive signal separates "ran and correctly found nothing" from "ran, silently failed to parse, dropped nothing"

Verified side by side on identical content:

```
asthma.AFR.tsv   (int POS)   counts={'n_in':2,'n_dropped':1,'n_out':1}  stderr='...DROP 1:5982778...'
bmi.AFR.PAGE.tsv (float POS) counts={'n_in':2,'n_dropped':0,'n_out':2}  stderr=''
```

**Neither module counts unparseable coordinates, neither warns**, and the audit invariant
`n_in - n_dropped == n_out` holds *perfectly* in the failure case.
`m3_occlusion_lockstep.smk:263-266` designates `counts.json` "the durable audit" and
`drops.log` "the in-run witness" — both are blind to this. **m3-04b's aggravation is making
`counts.json` the artifact of record for a rule in the production DAG.**

Every swallow path in the four newly-reachable modules is **fail-open** (keeps the row), so
the class is uniformly under-drop / under-count — no over-drops exist. Sites, by effect:

| site | swallowed condition | effect |
|---|---|---|
| `drop_occluded_from_sumstats.py:215-216` | unparseable coord | **under-drop**, clean `n_dropped==0` |
| `drop_occluded_from_sumstats.py:212` | short row | **under-drop**, silent |
| `occlusion_present_rate_scan.py:176-177` | unparseable coord | mis-counts *k* downward |
| `occlusion_present_rate_scan.py:172-173` | truncated row | mis-counts *k* downward |
| `occlusion_present_rate_scan.py:159` | blank first line | whole file scored "nothing present" — mis-counts *k* **and** *n* |
| `occlusion_manifest.py:397` | key absent | `pd.NA`, indistinguishable from "not scanned" |
| `run_native_ld_panel.py:826-833` | manifest append raises | region → excludelist-only, feeds **BLOCKER-4** |

`occlusion_span_filter.py:126-162` is the honourable exception and is **OK-VERIFIED**:
`parse_bim_row` raises loudly on `<6` fields or a non-integer bp, with no swallow anywhere
in `detect_occluded_variants`.
**PRE-EXISTING, AGGRAVATED.**

### D-04b-01 — full extent measured: exactly one file, but 100% of it

A complete streaming pass over all ten `*.AFR*.tsv.bgz` (no file materialized):

| file | POS format | body rows | rows failing `int(pos)` |
|---|---|---|---|
| **`bmi.AFR.PAGE.2019.GRCh37`** | **100% FLOAT** (`"56019.0"`) | 17,195,956 | **all 17,195,956** |
| `asthma.AFR` | integer | 19,695,660 | 0 |
| `hdl / ldl / tc / tg .AFR.GLGC.2021` | integer | ~19.75M each | 0 |
| `stroke.AFR` / `stroke.AFR.GIGASTROKE.2022` | integer | 5.26M / 10.80M | 0 |
| `t2d.AFR` | integer | 19,257,160 | 0 |
| `asthma.AFR.grch38_backup` (out of scan scope) | integer | 20,274,980 | 0 |

**Zero occurrences anywhere** of scientific notation, whitespace padding, empty/`NA`/`.`
positions, `chr` prefixes, or ragged rows. So the defect is *one file, totally* — not a
scattering. Two latent `int()` quirks exist (`"1_000"` → 1000, full-width digits accepted)
with no live exposure.

**The live bound is real but fragile.** The mirror rule's `stem=r"[A-Za-z0-9_.\-]+\.AFR"`
matches only `asthma.AFR`, `stroke.AFR`, `t2d.AFR` — all verified integer — while the
present-rate scan uses a *glob* that does include the float file. That asymmetry is what
confines today's damage to the published *k/n*. But `Snakefile:68-71` shows `run_finemap`
requests `bmi.AFR.tsv.bgz`, a canonical name that **does not exist on disk**. The moment
BMI-AFR is re-harmonized to it, the mirror matches and the same float POS becomes a silent
under-drop on a real `run_finemap` input. **Making a zero-caller module reachable from
production is itself the aggravation: the defect was inert and is now one filename away
from live.**

### MEDIUM-8 — non-atomic in-place writes; a truncated catalog is a silently *smaller* drop key
No temp-then-rename anywhere: `assemble_occlusion_catalog.py:414-420` writes `out_path`
**twice in place**; `drop_occluded_from_sumstats.py:196` and `occlusion_lockstep_cli.py:206,218`
open `out_path` directly. Verified — a catalog truncated by one row with a newer mtime
yields `{'n_in':3,'n_dropped':1,'n_out':2}` against a true `{3,2,1}`: clean, smaller, no
error. Two partial mitigations deserve credit: for an *empty* catalog `_load_manifest_keys`
fails **closed**, and Snakemake's incomplete-file metadata plus habitual `--rerun-incomplete`
help — but neither survives a lost `.snakemake` dir or a direct CLI call.

### MEDIUM-9 — `occlusion_filter_variants` has no commit barrier; the sumstats rule accidentally has one
`m3_occlusion_lockstep.smk:277-279` declares **two** outputs (`.bgz` + `.tbi`) with `tabix`
after `bgzip` under `set -euo pipefail`, so a mid-write kill leaves `.tbi` missing and forces
a rerun. `:336-337` declares **one** output written in place, so a truncated variant list
survives on mtime alone. Mirror the two-phase shape, or add a `.done` sentinel.

### MEDIUM-10 — `counts.json` describes the pre-compression temp file, not the delivered artifact
`occlusion_lockstep_cli.py:201-209` derives counts from the plain temp file, then bgzips it;
**nothing verifies the `.bgz` decompresses to `n_out` rows**. Verified the adjacent shape: a
valid-gzip-but-zero-content source yields `{'n_in':0,'n_dropped':0,'n_out':0}` with the
invariant **holding** and a 0-byte mirror. This is the `_SUCCESS marker is NOT evidence of
data` pattern exactly — the audit invariant is satisfied by an empty artifact.

### MEDIUM-1 — a stale or empty catalog under-drops silently and is indistinguishable from a correct no-op
Manifest inputs resolve by a **parse-time glob** (`m3_occlusion_lockstep.smk:163-174`), and
the file documents that an existing catalog must be deleted for new rows to roll up. An
empty catalog yields a byte-identical mirror and `n_dropped: 0` — which the module defines
as a *valid* no-op. Confirmed: `{'n_in': 2, 'n_dropped': 0, 'n_out': 2}`. There is no gate
distinguishing "nothing to drop" from "catalog was never rebuilt".
**NEWLY-INTRODUCED.**

### MEDIUM-2 — a partial `occlusion_lockstep` config block validates clean and silently activates hardcoded defaults
The new schema (`pipeline.schema.yaml:344-374`) has **no `required:`**, no nested
`additionalProperties: false`, and no `enum` on `ancestries`. Misspelling `ancestries`, or
writing `ancestries: [afr]` (lowercase — the resolver compares case-sensitively), validates
and silently reverts to legacy paths. This is precisely what the module's own docstring
(`occlusion_lockstep_cli.py:52-56`) declares forbidden. A silent no-op on a pre-registered
policy is the worst failure mode for this block. **NEWLY-INTRODUCED.**

### MEDIUM-3 — the documented kill switch is unreachable from the CLI and fails closed on the whole workflow
`config/pipeline.yaml:258` documents `enabled: false` as "the kill switch". Via `--config`,
Snakemake parses the nested value as a string and the new schema hard-rejects it:
`ValidationError: 'false' is not of type 'boolean'`. An operator reaching for the emergency
switch under pressure gets a total workflow failure, not a fallback. Only a YAML overlay
works. **NEWLY-INTRODUCED.**

### MEDIUM-4 — path defaults are duplicated in two independent reconstructions
`occlusion_lockstep_cli.py:93-94` vs `m3_occlusion_lockstep.smk:118,121`. Consumer and
producer build the same path from separate literals that merely happen to agree. Changing
one silently desynchronizes them (loudly, as a `MissingRuleException` — hence MEDIUM).
**NEWLY-INTRODUCED.**

### MEDIUM-5 — asymmetric project-root resolution; a comment describes code that does not exist
`m3_occlusion_lockstep.smk:75-86` implements a real walk-up. `finemap.smk:52-59` does not —
despite its comment at `:47-51` explicitly claiming "we walk up if `src/python` is not
directly under it". Demonstrated live: `tests/toy_3locus/Snakefile.test` fails with
`ModuleNotFoundError: No module named 'ld_panel'`. **PRE-EXISTING, AGGRAVATED** (m3-04b
added a second import on the same known-false mechanism and cited the rationale approvingly).

### MEDIUM-6 — the SH2B3 subregion may be rejected on coverage, falling to identity with no artifact
The crosswalk maps `SH2B3_12q24` to a deliberately *narrower* subregion.
`run_susie_rss.R:184` gates on `overlap >= MIN_LD_OVERLAP && coverage >= MIN_LD_COVERAGE`.
If the sub-window covers less of the curated region than the threshold, the panel is
rejected and the job falls to identity with only a message. **Check explicitly at the
region-1 validation gate.**

### MEDIUM-7 — the m3-04c `snakemake --dry-run --quiet` acceptance criterion is unsatisfiable pre-fire, in BOTH tasks
`data/processed/ld_reference/` does not exist, so `resolve_ld_path` raises rather than
returning a tail path — proven for the pre-crosswalk id *and* the post-crosswalk id. D-04b-03
assigned this to "m3-04c to discharge", but **Task 1 does not discharge it** — the crosswalk
changes *which* nonexistent path is requested, not whether one exists. The escape hatch here
is an executor touching fake `.rds` files. **PRE-EXISTING, mis-assigned.**

### LOW-1 — the catalog scan double-counts `stroke`
The parse-time glob resolves 9 files but only **8 distinct traits** (both `stroke.AFR` and
`stroke.AFR.GIGASTROKE.2022.GRCh37` are included), inflating the present-rate `k/n`
denominator the pre-registration publishes. Adjacent to but distinct from D-04b-01.

### LOW-2 — `{catalog}.README.md` is an undeclared Snakemake output
Written by `assemble_occlusion_catalog.py:426`, mentioned only in a docstring. Untracked,
not cleaned on failure, can drift from the catalog beside it.

### LOW-4 — degraded records are not de-duplicated
`_region_id_from_excludelist` uses the basename only
(`assemble_occlusion_catalog.py:152-192`), so the same region reached via two directories
yields duplicate rows (verified: `n_variants: 2` for 1 distinct variant), inflating the
published census. `aggregate_manifests` dedups on `(region_id, variant_id)`; the degraded
path bypasses it. Harmless to the drop itself.

### LOW-5 — chrX encoding is split across the AFR corpus (latent)
`asthma.AFR` uses the strings `X`/`Y`; `bmi.AFR.PAGE` and the grch38 backup use `23`/`24`/`25`.
`_canonical_key` maps `"X"` → `'X'` (str) and `"23"` → `23` (int), which can never compare
equal — a silent no-match. **Out of scope today** (the 276 AFR regions are chr1–22 only), but
it converts to a live under-drop the moment a chrX region enters the panel.

### LOW-3 — the `stem` constraint excludes the long-form AFR filenames
`bmi.AFR.PAGE.2019.GRCh37`, the GLGC lipids and `stroke.AFR.GIGASTROKE…` can never be
mirrored. Harmless today because `run_finemap` only requests the short form — but it is an
unstated coupling.

---

## 3. Gate binding — what blocks what

| Gate | Blocked by | Autonomous? |
|---|---|---|
| **m3-04c merge (T1+T2)** | BLOCKER-2 (self-contradicting test), BLOCKER-3 (stale line numbers / misplaced guard), MEDIUM-7 (unsatisfiable dry-run criterion) | Yes — `$0`, NC State, but each needs a deliberate decision, not an executor's improvisation |
| **The ~11-day billed fire** | **BLOCKER-1 (the panel is still unread)**, HIGH-1 (`allow_degraded` dead-end), HIGH-2 (silent Path-2 revert) | **No — BLOCKER-1 needs a scope decision from Carter** |
| **Trusting the post-fire catalog as a drop key** | **BLOCKER-4 (partial rollup silently drops excludelist-only regions)** | Yes — `$0`, and it should land *before* the fire |
| **Publishing the pre-registered `k/n`** | HIGH-0 (guard cannot fire), HIGH-4 (no unparseable counter), D-04b-01, LOW-1 (`stroke` double-count) | Yes — `$0` |
| **The first long / interruptible run** | MEDIUM-8 (atomicity), MEDIUM-9 (variants commit barrier), MEDIUM-10 (`.bgz` unverified) | Yes — `$0` |
| **Region-1 validation gate** | MEDIUM-6 (SH2B3 coverage rejection) | Carter, in-perimeter |
| **The OSF pre-registration provenance claim** | HIGH-3 (no panel-side audit artifact) | Partly autonomous |
| **Nothing (already merged)** | every item in §1 | — |

**Watch-items that convert to live defects on a specific trigger:** D-04b-01 and LOW-5 both
go live the moment BMI-AFR is re-harmonized to `bmi.AFR.tsv.bgz` or a chrX region enters the
panel. Neither is live today.

**Nothing here blocks what has already merged.** m3-04b is sound on the axis it claims:
EUR and Track-A numerics are provably immovable, the DAG is clean, the seam is completely
and symmetrically wired, and the test suite is honest. No revert is warranted.

---

## 4. Recommended sequence (revised)

1. **Do not execute m3-04c as written.** Its headline must_have is false as specified, and
   its Task 1 acceptance criteria are unsatisfiable (BLOCKER-2, MEDIUM-7).
2. **Carter decides the BLOCKER-1 remedy** — thread `{input.ld_matrix}` into
   `run_susie_rss.R` behind a new `--ld-file`, add a promote/symlink rule from `AFR_aou/`
   into the read path, or make `ld_dir` per-ancestry-source. **This is the only genuine fork
   and the only thing that needs Carter.** Recommendation: the `--ld-file` thread, because it
   makes the resolver the single source of truth and removes the declare/read split
   permanently rather than papering over it; it does touch a frozen-adjacent R script, which
   is why it is Carter's call and not mine.
3. **Replan m3-04c** around that decision: re-anchor every `finemap.smk` line number to
   `2bda675`, fold the test rewrite (BLOCKER-2) in as an explicit reviewed task rather than
   leaving it as an executor's improvisation, and strike the unsatisfiable dry-run criterion
   citing D-04b-03.
4. **Land BLOCKER-4 and HIGH-0/HIGH-4 first — they are autonomous, `$0`, and independent of
   the fork.** A region-coverage assertion (or manifest∪excludelist union) plus an
   unparseable-coordinate counter surfaced in `counts.json` and the catalog. These make the
   post-fire catalog trustworthy as a drop key, and they are cheap now and expensive after
   11 days of compute.
5. **Then** m3-04c T1+T2 autonomously, `$0`.
6. **Before the fire:** settle HIGH-1 (record the `allow_degraded` decision *in* the gate),
   HIGH-2 (make Path 2 set a flag, and have something actually read it), and MEDIUM-8/9/10
   (atomicity and post-write verification — these are preconditions on any long
   interruptible run, which an 11-day fire certainly is).
7. **Fire only after BLOCKER-1 is closed.** Otherwise the panel stays unread and the
   ~$385–1,084 buys nothing — which is the exact outcome the m3-04 replan existed to prevent.

---

## 5. Process notes

**A concurrent session touched `finemap.smk` during the sweep.** One probe transiently
observed `NameError: name 'CURATED_TO_M2' is not defined` at `finemap.smk:174` — a symbol
that exists nowhere in `src/`, only in the m3-04c plan. The file's mtime is
`2026-08-04 01:52:38`, yet its md5 matches HEAD exactly. Two investigators disclosed making
transient simulated edits and reverting them, which is the most likely explanation and is
consistent with the verified-clean end state. **Verified at report time: `finemap.smk` md5
worktree == md5 HEAD, no tracked modifications, no live `snakemake` processes.** Flagged
because m3-04b's docstring claims wave sequencing prevents the two `finemap.smk` edits from
colliding — worth remembering when m3-04c executes.

**Benchmark churn is expected.** `tests/m3/sparse_parent_benchmark.tsv` is rewritten by every
suite run (timing columns only) and is not a real change.
