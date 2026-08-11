# quick/260811-pmv — EVIDENCE LOG (SR4-OPEN)

**The raw evidence log. Every command, verbatim, with its unedited output and
its exit code.** This file is the single source of truth for
`260811-pmv-DOSSIER.md`: no number appears in the dossier that is not produced
by a command recorded here.

**Interpretation does not happen in this file.** It happens in the dossier. The
only interpretive content below is STEP 7's mechanical derivation, which is
recorded here so the dossier transcribes rather than invents.

- **Measured at:** HEAD `b945c595` on branch `m3-W2-aou-deltas`, 2026-08-11.
- **Everything is read-only.** No `src/`, `tests/`, `config/`, `DECISIONS.md`,
  `HANDOFF.json` or `STATE.md` file was written. `$0`; no LSF, no `gsutil` /
  `gcloud` / `bq` / `dataproc` / `hailctl` / `wb`, no perimeter contact.
- **`results/` was NEVER searched.** It and `results/legacy/` are symlinks into
  `/rs1` which `grep -r` does not follow on this tree; they contain none of the
  eight subject paths. Every scoped search below is `.planning/ src/ tests/ config/`.
- **⚠ `git log -S` is BANNED as a primary method here** and is run exactly once,
  as a demonstration of the trap, with its `rc` recorded (STEP 5b).

## The subjects

| ID | Path | Role |
|---|---|---|
| F1 | `src/python/occlusion_manifest.py` | subject |
| F2 | `src/python/occlusion_present_rate_scan.py` | subject |
| F3 | `src/python/drop_occluded_from_sumstats.py` | subject |
| F4 | `src/scripts/ld_npz_to_rds.R` | subject |
| F5 | `src/snakemake/schemas/pipeline.schema.yaml` | subject |
| C1 | `src/python/plink_ld_to_npz.py` | **control** — must be 0-diff |
| C2 | `src/python/condition_ld_matrix.py` | **control** — must be 0-diff |
| C3 | `src/python/occlusion_span_filter.py` | **control** — must be 0-diff |

The pin under test is **`bf16289`**.

---

## STEP 0 — the frame

`$ date -u`

```
Tue Aug 11 10:55:27 PM UTC 2026
```
rc=0

`$ git rev-parse HEAD`

```
b945c5958ec8a46bb53d24698f0de49641a1d221
```
rc=0

`$ git status --porcelain`

```
?? .planning/debug/m3-producer-unbounded-dense-read.md
?? .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v4_addendum_supervisor_orphan.json
?? .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/bjobs.tsv
?? .planning/quick/260501-wdn-w5-aggregator-figure-refresh-frozen-numb/
?? .planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/260502-lsk-PLAN.md
?? results/track_a_aggregations/phase5_overview.tsv
?? results_lsweep_L15.preFix.bak.20260429_215312/
?? results_lsweep_L15.preNiter500.bak.20260429_213644/
?? results_lsweep_L20.preFix.bak.20260429_215312/
?? results_lsweep_L20.preNiter500.bak.20260429_213644/
?? results_lsweep_L30.preFix.bak.20260429_215312/
?? results_lsweep_L30.preNiter500.bak.20260429_213644/
?? targeted_rerun_figures/
?? targeted_rerun_jobs/
?? targeted_rerun_logs/
?? targeted_rerun_outputs/
?? targeted_rerun_package_20260507_222752.zip
?? targeted_rerun_reports/
?? targeted_rerun_scripts/
?? targeted_rerun_tables/
```
rc=0

`$ git cat-file -t bf16289`

```
commit
```
rc=0

### The untracked baseline (persisted OUTSIDE the repo)

The measuring instrument must not be a member of the set it measures, so the
baseline lives outside the working tree.

`$ echo "TMPDIR=${TMPDIR:-UNSET}"`

```
TMPDIR=/share/clintonlab/ckclinto/tmp
```
rc=0

`$ BASE=${TMPDIR:-/tmp}/260811-pmv-untracked-baseline.txt; echo "$BASE"; wc -l "$BASE"`

```
/share/clintonlab/ckclinto/tmp/260811-pmv-untracked-baseline.txt
20 /share/clintonlab/ckclinto/tmp/260811-pmv-untracked-baseline.txt
```
rc=0

`$ cat ${TMPDIR:-/tmp}/260811-pmv-untracked-baseline.txt`

```
.planning/debug/m3-producer-unbounded-dense-read.md
.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v4_addendum_supervisor_orphan.json
.planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/bjobs.tsv
.planning/quick/260501-wdn-w5-aggregator-figure-refresh-frozen-numb/
.planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/260502-lsk-PLAN.md
results_lsweep_L15.preFix.bak.20260429_215312/
results_lsweep_L15.preNiter500.bak.20260429_213644/
results_lsweep_L20.preFix.bak.20260429_215312/
results_lsweep_L20.preNiter500.bak.20260429_213644/
results_lsweep_L30.preFix.bak.20260429_215312/
results_lsweep_L30.preNiter500.bak.20260429_213644/
results/track_a_aggregations/phase5_overview.tsv
targeted_rerun_figures/
targeted_rerun_jobs/
targeted_rerun_logs/
targeted_rerun_outputs/
targeted_rerun_package_20260507_222752.zip
targeted_rerun_reports/
targeted_rerun_scripts/
targeted_rerun_tables/
```
rc=0

## STEP 1 — what `bf16289` actually IS

`$ git log -1 --format='%H%n%ad%n%s' bf16289`

```
bf16289dacaa67c978977d378b132e73ac9adb69
Thu Jul 16 01:44:30 2026 -0400
docs(handoff): 2026-07-16 close-session — m3-07 CODE-COMPLETE; unambiguous resume point
```
rc=0

`$ git show --stat --oneline --format='' bf16289 | head -40`

```
 .../m3-aou-afr-ld-panel-build/.continue-here.md    | 22 +++++++++++++++++++---
 1 file changed, 19 insertions(+), 3 deletions(-)
```
rc=0

`$ git show --name-only --format='' bf16289 | wc -l`

```
1
```
rc=0

### Did `bf16289` itself touch any of the five?

`$ git show --name-only --format='' bf16289 | grep -c 'src/python/occlusion_manifest.py'`

```
0
```
rc=1

`$ git show --name-only --format='' bf16289 | grep -c 'src/python/occlusion_present_rate_scan.py'`

```
0
```
rc=1

`$ git show --name-only --format='' bf16289 | grep -c 'src/python/drop_occluded_from_sumstats.py'`

```
0
```
rc=1

`$ git show --name-only --format='' bf16289 | grep -c 'src/scripts/ld_npz_to_rds.R'`

```
0
```
rc=1

`$ git show --name-only --format='' bf16289 | grep -c 'src/snakemake/schemas/pipeline.schema.yaml'`

```
0
```
rc=1

### ...and the three controls?

`$ git show --name-only --format='' bf16289 | grep -c 'src/python/plink_ld_to_npz.py'`

```
0
```
rc=1

`$ git show --name-only --format='' bf16289 | grep -c 'src/python/condition_ld_matrix.py'`

```
0
```
rc=1

`$ git show --name-only --format='' bf16289 | grep -c 'src/python/occlusion_span_filter.py'`

```
0
```
rc=1

## STEP 2 — diffstat TODAY, all EIGHT

### THE FIVE (subjects)

`$ git diff --numstat bf16289 HEAD -- src/python/occlusion_manifest.py`

```
46	8	src/python/occlusion_manifest.py
```
rc=0

`$ git diff --numstat bf16289 HEAD -- src/python/occlusion_present_rate_scan.py`

```
154	21	src/python/occlusion_present_rate_scan.py
```
rc=0

`$ git diff --numstat bf16289 HEAD -- src/python/drop_occluded_from_sumstats.py`

```
97	24	src/python/drop_occluded_from_sumstats.py
```
rc=0

`$ git diff --numstat bf16289 HEAD -- src/scripts/ld_npz_to_rds.R`

```
313	62	src/scripts/ld_npz_to_rds.R
```
rc=0

`$ git diff --numstat bf16289 HEAD -- src/snakemake/schemas/pipeline.schema.yaml`

```
119	0	src/snakemake/schemas/pipeline.schema.yaml
```
rc=0

### THE THREE (control — these MUST be empty)

`$ git diff --numstat bf16289 HEAD -- src/python/plink_ld_to_npz.py`

```
```
rc=0

`$ git diff --numstat bf16289 HEAD -- src/python/condition_ld_matrix.py`

```
```
rc=0

`$ git diff --numstat bf16289 HEAD -- src/python/occlusion_span_filter.py`

```
```
rc=0

### The control as one command

`$ git diff --numstat bf16289 HEAD -- src/python/plink_ld_to_npz.py src/python/condition_ld_matrix.py src/python/occlusion_span_filter.py`

```
```
rc=0

## STEP 3 — the full commit history since the pin

`$ git log --format='%h|%ad|%an|%s' --date=short bf16289..HEAD -- src/python/occlusion_manifest.py`

```
bf963df|2026-08-04|Carter K. Clinton|feat(260804-rtc-T2): unparseable counters (HIGH-4) + a total-miss guard that can fire (HIGH-0)
3bb8783|2026-08-04|Carter K. Clinton|fix(260804-rtc-T1): ONE shared integral-position coercion + canonical key (D-04b-01)
```
rc=0

`$ git log --format='%h' bf16289..HEAD -- src/python/occlusion_manifest.py | wc -l`

```
2
```
rc=0

`$ git log --format='%h|%ad|%an|%s' --date=short bf16289..HEAD -- src/python/occlusion_present_rate_scan.py`

```
fac9a93|2026-08-04|Carter K. Clinton|feat(260804-rtc-T3): region-coverage assertion (BLOCKER-4), LOW-1 visibility, measured k/n
bf963df|2026-08-04|Carter K. Clinton|feat(260804-rtc-T2): unparseable counters (HIGH-4) + a total-miss guard that can fire (HIGH-0)
3bb8783|2026-08-04|Carter K. Clinton|fix(260804-rtc-T1): ONE shared integral-position coercion + canonical key (D-04b-01)
```
rc=0

`$ git log --format='%h' bf16289..HEAD -- src/python/occlusion_present_rate_scan.py | wc -l`

```
3
```
rc=0

`$ git log --format='%h|%ad|%an|%s' --date=short bf16289..HEAD -- src/python/drop_occluded_from_sumstats.py`

```
bf963df|2026-08-04|Carter K. Clinton|feat(260804-rtc-T2): unparseable counters (HIGH-4) + a total-miss guard that can fire (HIGH-0)
3bb8783|2026-08-04|Carter K. Clinton|fix(260804-rtc-T1): ONE shared integral-position coercion + canonical key (D-04b-01)
```
rc=0

`$ git log --format='%h' bf16289..HEAD -- src/python/drop_occluded_from_sumstats.py | wc -l`

```
2
```
rc=0

`$ git log --format='%h|%ad|%an|%s' --date=short bf16289..HEAD -- src/scripts/ld_npz_to_rds.R`

```
57b381f|2026-08-05|Carter K. Clinton|feat(260805-23d-T5): drop the dense ld field, bound the converter read (BLOCKER-D, PARTIAL)
```
rc=0

`$ git log --format='%h' bf16289..HEAD -- src/scripts/ld_npz_to_rds.R | wc -l`

```
1
```
rc=0

`$ git log --format='%h|%ad|%an|%s' --date=short bf16289..HEAD -- src/snakemake/schemas/pipeline.schema.yaml`

```
2563451|2026-08-06|Carter K. Clinton|feat(260805-w7u-T1): route the coloc LD path through the resolver; make the manifest fail loudly (FINDING E)
64f420a|2026-08-05|Carter K. Clinton|feat(260805-o7o-T2): AFR-gated allele-aware join, z orientation flip, counted JSON (FINDING H, wiring half)
57b381f|2026-08-05|Carter K. Clinton|feat(260805-23d-T5): drop the dense ld field, bound the converter read (BLOCKER-D, PARTIAL)
aeed8c0|2026-08-05|Carter K. Clinton|feat(260805-23d-T1): ancestry-gate the LD read path (BLOCKER-B, half 1 of 2)
d7dfa67|2026-08-03|Carter K. Clinton|feat(m3-04b-T1): genome-wide occlusion catalog assembler + Snakemake rule
```
rc=0

`$ git log --format='%h' bf16289..HEAD -- src/snakemake/schemas/pipeline.schema.yaml | wc -l`

```
5
```
rc=0

### The union of drift commits across the five

`$ git log --format='%h|%ad|%s' --date=short bf16289..HEAD -- src/python/occlusion_manifest.py src/python/occlusion_present_rate_scan.py src/python/drop_occluded_from_sumstats.py src/scripts/ld_npz_to_rds.R src/snakemake/schemas/pipeline.schema.yaml`

```
2563451|2026-08-06|feat(260805-w7u-T1): route the coloc LD path through the resolver; make the manifest fail loudly (FINDING E)
64f420a|2026-08-05|feat(260805-o7o-T2): AFR-gated allele-aware join, z orientation flip, counted JSON (FINDING H, wiring half)
57b381f|2026-08-05|feat(260805-23d-T5): drop the dense ld field, bound the converter read (BLOCKER-D, PARTIAL)
aeed8c0|2026-08-05|feat(260805-23d-T1): ancestry-gate the LD read path (BLOCKER-B, half 1 of 2)
fac9a93|2026-08-04|feat(260804-rtc-T3): region-coverage assertion (BLOCKER-4), LOW-1 visibility, measured k/n
bf963df|2026-08-04|feat(260804-rtc-T2): unparseable counters (HIGH-4) + a total-miss guard that can fire (HIGH-0)
3bb8783|2026-08-04|fix(260804-rtc-T1): ONE shared integral-position coercion + canonical key (D-04b-01)
d7dfa67|2026-08-03|feat(m3-04b-T1): genome-wide occlusion catalog assembler + Snakemake rule
```
rc=0
## STEP 4 — provenance, per commit

Eight distinct commits touch the five since `bf16289` (STEP 3 union).
TRACEABLE requires BOTH: (a) the subject carries a GSD task token that
resolves to a real artifact directory, AND (b) the commit's short SHA is
NAMED inside that artifact.

### (a) — do the task tokens resolve to real artifact directories?

`$ ls -d .planning/quick/*260804-rtc*`

```
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo
```
rc=0

`$ ls -d .planning/quick/*260805-23d*`

```
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran
```
rc=0

`$ ls -d .planning/quick/*260805-o7o*`

```
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle
```
rc=0

`$ ls -d .planning/quick/*260805-w7u*`

```
.planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t
```
rc=0

`$ ls .planning/phases/m3-aou-afr-ld-panel-build/ | grep 'm3-04b'`

```
m3-04b-BLAST-RADIUS.md
m3-04b-W4-occlusion-catalog-and-consume-seam-PLAN.md
m3-04b-W4-SUMMARY.md
```
rc=0

### (b) — is each commit's short SHA NAMED inside its artifact?

⚠ (b) is the load-bearing half: a token in a commit subject is a CLAIM BY
THE COMMIT AUTHOR; the SHA appearing in a SUMMARY/PLAN is THE REVIEWED
RECORD NAMING IT.

#### commit `3bb8783` vs `.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo`

`$ grep -rn '3bb8783' .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo | wc -l`

```
1
```
rc=0

`$ grep -rln '3bb8783' .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo`

```
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md
```
rc=0

`$ grep -rn '3bb8783' .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo | head -6`

```
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md:63:| T1 | `3bb8783` | `occlusion_coord_key` + three delegating call sites (D-04b-01) |
```
rc=0

#### commit `bf963df` vs `.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo`

`$ grep -rn 'bf963df' .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo | wc -l`

```
1
```
rc=0

`$ grep -rln 'bf963df' .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo`

```
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md
```
rc=0

`$ grep -rn 'bf963df' .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo | head -6`

```
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md:64:| T2 | `bf963df` | unparseable/truncated counters (HIGH-4) + a substance guard (HIGH-0) |
```
rc=0

#### commit `fac9a93` vs `.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo`

`$ grep -rn 'fac9a93' .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo | wc -l`

```
1
```
rc=0

`$ grep -rln 'fac9a93' .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo`

```
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md
```
rc=0

`$ grep -rn 'fac9a93' .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo | head -6`

```
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md:65:| T3 | `fac9a93` | region-coverage assertion (BLOCKER-4), LOW-1 visibility, measured k/n |
```
rc=0

#### commit `57b381f` vs `.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran`

`$ grep -rn '57b381f' .planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran | wc -l`

```
2
```
rc=0

`$ grep -rln '57b381f' .planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran`

```
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-SUMMARY.md
```
rc=0

`$ grep -rn '57b381f' .planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran | head -6`

```
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-SUMMARY.md:147:| 5 | `57b381f` | D (partial) | dense `ld` field dropped from the `.rds` payload; block-tiled `convert=FALSE` reticulate read; `mem_mb` 8000 → config `m3_convert_mem_mb` (64000), `runtime` 120 → 480, fail-fast `m3_convert_max_n_var` ceiling (120000) |
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-SUMMARY.md:345:- All 8 referenced commits resolve (`aeed8c0`, `51a60ca`, `ab19186`, `6643c19`, `57b381f`, `7f24b4d`, `5ec33bd`, `3f431ab`).
```
rc=0

#### commit `aeed8c0` vs `.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran`

`$ grep -rn 'aeed8c0' .planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran | wc -l`

```
3
```
rc=0

`$ grep -rln 'aeed8c0' .planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran`

```
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-SUMMARY.md
```
rc=0

`$ grep -rn 'aeed8c0' .planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran | head -6`

```
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-SUMMARY.md:143:| 1 | `aeed8c0` | B (crosswalk half) | `src/python/ld_read_path.py` (new pure gate); `ld_read_path: {enabled: true, ancestries: [AFR]}` in `config/pipeline.yaml` + matching schema entry; `finemap.smk` routes `input.ld_matrix` through `ld_matrix_region_id` and renders `--ld-authoritative {params.ld_authoritative}`; `run_susie_rss.R` DECLARES and strictly PARSES the flag |
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-SUMMARY.md:282:- **Verdict:** genuine replace-not-relax. Recorded here as an authorized second edit, **not** papered over and **not** a defect. Documented in `aeed8c0`'s commit body as deviation 2 at the time it was made.
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-SUMMARY.md:345:- All 8 referenced commits resolve (`aeed8c0`, `51a60ca`, `ab19186`, `6643c19`, `57b381f`, `7f24b4d`, `5ec33bd`, `3f431ab`).
```
rc=0

#### commit `64f420a` vs `.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle`

`$ grep -rn '64f420a' .planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle | wc -l`

```
2
```
rc=0

`$ grep -rln '64f420a' .planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle`

```
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-VERIFICATION.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-SUMMARY.md
```
rc=0

`$ grep -rn '64f420a' .planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle | head -6`

```
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-VERIFICATION.md:17:**Commits reviewed:** `10c14f2` (T1), `64f420a` (T2), `dc4bbd2` (T3), `fb839a4` (docs) — HEAD is
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-SUMMARY.md:67:| 2 | `64f420a` | allow-list gate, argv thread, z flip, allele-keyed catalog join, counted JSON (wiring half) |
```
rc=0

#### commit `2563451` vs `.planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t`

`$ grep -rn '2563451' .planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t | wc -l`

```
2
```
rc=0

`$ grep -rln '2563451' .planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t`

```
.planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t/260805-w7u-SUMMARY.md
```
rc=0

`$ grep -rn '2563451' .planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t | head -6`

```
.planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t/260805-w7u-SUMMARY.md:77:| 1 | `2563451` | resolver-routed `_qtl_coloc_ld_input`; the single gate; the non-path manifest sentinel |
.planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t/260805-w7u-SUMMARY.md:837:(`2563451`, `1815bfd`) verified present in `git log`. Nothing claimed that does not exist.
```
rc=0

#### commit `d7dfa67` vs `.planning/phases/m3-aou-afr-ld-panel-build`

`$ grep -rn 'd7dfa67' .planning/phases/m3-aou-afr-ld-panel-build | wc -l`

```
6
```
rc=0

`$ grep -rln 'd7dfa67' .planning/phases/m3-aou-afr-ld-panel-build`

```
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md
.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md
```
rc=0

`$ grep -rn 'd7dfa67' .planning/phases/m3-aou-afr-ld-panel-build | head -6`

```
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md:64:| `d7dfa67` | T1 GREEN | assembler + `m3_assemble_occlusion_catalog` + config/schema/env |
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md:197:* **Commit:** `d7dfa67`.
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md:209:* **Commit:** `d7dfa67`.
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md:355:Commits verified in `git log`: `a6dc3a3`, `d7dfa67`, `0cae502`, `37c51df`.
.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md:203:> **★ m3-04b LANDED** (`d7dfa67` T1 + `0cae502`/`37c51df` T2 + `f038ce0` docs). T1 = `assemble_occlusion_catalog.py`, the FIRST production caller for the four zero-caller m3-07 functions. T2 = the lockstep seam (`occlusion_lockstep_cli.py` + `m3_occlusion_lockstep.smk`) wiring BOTH `run_finemap.input.sumstats` AND `input.variants`, AFR-gated so EUR/Track-A strings stay byte-identical. **`tests/m3` 420P/31S/0F → 444P/31S/0F**, re-run by the orchestrator at HEAD (422.66s). All 7 pinned files 0-line diff.
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md:4:**Assessed at:** HEAD `2bda675` (m3-04b landed: `d7dfa67`, `0cae502`, `37c51df`, `f038ce0`)
```
rc=0

### Contents of each artifact directory (so a reader can see what was searched)

`$ ls .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo`

```
260804-rtc-PLAN.md
260804-rtc-SUMMARY.md
260804-rtc-VERIFICATION.md
measure_present_rate_kn.json
measure_present_rate_kn.log
measure_present_rate_kn.py
```
rc=0

`$ ls .planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran`

```
260805-23d-PLAN.md
260805-23d-SUMMARY.md
```
rc=0

`$ ls .planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle`

```
260805-o7o-PLAN.md
260805-o7o-SUMMARY.md
260805-o7o-VERIFICATION.md
```
rc=0

`$ ls .planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t`

```
260805-w7u-PLAN.md
260805-w7u-SUMMARY.md
260805-w7u-VERIFICATION.md
```
rc=0

`$ ls .planning/phases/m3-aou-afr-ld-panel-build | head -40`

```
cohort_summary_m3.NOTES.md
cohort_summary_m3.tsv
deferred-items.md
DRAFT-orderingB-band-before-checkpoint.md
DURABLE-FIX-DESIGN-atomic-final-write.md
e2-exposure-measure.R
e2-exposure-real-corpus.tsv
e2-exposure-track-a-regions.tsv
m3-00-W0-foundations-PLAN.md
m3-00-W0-foundations-SUMMARY.md
m3-01-W1-aou-cohort-and-hard-gates-PLAN.md
m3-01-W1-aou-cohort-and-hard-gates-SUMMARY.md
m3-02b-W2-rescope-BLAST-RADIUS-FIX.md
m3-02b-W2-rescope-REVIEW-FIX.md
m3-02b-W2-rescope-REVIEW.md
m3-02b-W2-rescope-split-stitch-code-PLAN.md
m3-02b-W2-rescope-split-stitch-code-SUMMARY.md
m3-02c-W2-rescope-quota-probe-and-gonogo-PLAN.md
m3-02d-REPROBE-BRIEF.md
m3-02d-W2-rescope-write-egress-split-PLAN.md
m3-02e-AFR-NATIVE-FIRE-BRIEF.md
m3-02e-W2-native-ld-export-and-public-eur-PLAN.md
m3-02e-W2-native-ld-export-and-public-eur-SUMMARY.md
m3-02-W2-DESIGN-DELTA.md
m3-02-W2-dev-fire-and-validation-PLAN.md
m3-02-W2-dev-fire-and-validation-SUMMARY.md
m3-03-W3-ncsu-ingest-and-resolver-PLAN.md
m3-03-W3-ncsu-ingest-and-resolver-SUMMARY.md
m3-04b-BLAST-RADIUS.md
m3-04b-W4-occlusion-catalog-and-consume-seam-PLAN.md
m3-04b-W4-SUMMARY.md
m3-04c-BLAST-RADIUS.md
m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md
m3-04-W4-production-and-egress-PLAN.md
m3-05-W5-closeout-and-osf-PLAN.md
m3-06-W6-ld-nan-psd-conditioning-PLAN.md
m3-06-W6-ld-nan-psd-conditioning-SUMMARY.md
m3-07a-UAT.md
m3-07a-W7-osf-gate-and-red-scaffold-PLAN.md
m3-07a-W7-osf-gate-and-red-scaffold-SUMMARY.md
```
rc=0
## STEP 5a — DECISIONS.md, the authoritative register

The ABSENCE of an entry is the key evidence here, so it is a MEASURED zero
with its command shown -- never an assertion.

`$ wc -l .planning/DECISIONS.md`

```
1250 .planning/DECISIONS.md
```
rc=0

`$ grep -c 'occlusion_manifest.py' .planning/DECISIONS.md`

```
0
```
rc=1

`$ grep -c 'occlusion_present_rate_scan.py' .planning/DECISIONS.md`

```
0
```
rc=1

`$ grep -c 'drop_occluded_from_sumstats.py' .planning/DECISIONS.md`

```
0
```
rc=1

`$ grep -c 'ld_npz_to_rds.R' .planning/DECISIONS.md`

```
0
```
rc=1

`$ grep -c 'pipeline.schema.yaml' .planning/DECISIONS.md`

```
0
```
rc=1

### ...and with line numbers (empty output = the measured zero)

`$ grep -n 'occlusion_manifest.py' .planning/DECISIONS.md`

```
```
rc=1

`$ grep -n 'occlusion_present_rate_scan.py' .planning/DECISIONS.md`

```
```
rc=1

`$ grep -n 'drop_occluded_from_sumstats.py' .planning/DECISIONS.md`

```
```
rc=1

`$ grep -n 'ld_npz_to_rds.R' .planning/DECISIONS.md`

```
```
rc=1

`$ grep -n 'pipeline.schema.yaml' .planning/DECISIONS.md`

```
```
rc=1

### Does the register mention the pin SHA at all?

`$ grep -c 'bf16289' .planning/DECISIONS.md`

```
3
```
rc=0

`$ grep -n 'bf16289' .planning/DECISIONS.md`

```
1058:  at `bf16289` — whole-file plus all **22** top-level symbols (13 + 3 + 6),
1060:  `bf16289` was enforced by **zero** tests anywhere in the repository.
1160:  `DECISIONS.md` entry, and `bf16289` enforced by zero tests.
```
rc=0

### Is `DEC-2026-08-06-sr4-freeze-scope` the ONLY freeze entry in the register?

`$ grep -n '^## .*freeze\|^## .*froz\|^## .*pin\|^## .*Freeze\|^## .*Pin' .planning/DECISIONS.md`

```
70:## 2026-04-09 — Scope tier: T1 spine in full + T1→T2 checkpoint
880:## 2026-05-03 — DEC-2026-05-03-vcl-Item2: Aggregator freeze locked at Wave 5 R2-merge state (md5 558fca45…)
1039:## 2026-08-06 — DEC-2026-08-06-sr4-freeze-scope: the source freeze is a CODE pin, not a byte pin; comments are deliberately FREE
```
rc=0

`$ grep -n 'DEC-2026-08-06-sr4-freeze-scope' .planning/DECISIONS.md`

```
1039:## 2026-08-06 — DEC-2026-08-06-sr4-freeze-scope: the source freeze is a CODE pin, not a byte pin; comments are deliberately FREE
```
rc=0

### The `DEC-2026-08-06-sr4-freeze-scope` entry, verbatim

`$ awk '/^## DEC-2026-08-06-sr4-freeze-scope/{f=1} f&&/^## /&&!/^## DEC-2026-08-06-sr4-freeze-scope/{if(++n>1)exit} f' .planning/DECISIONS.md`

```
```
rc=0

## STEP 5b — the narrative record, walked with a PRESENCE-CHECKED loop

⚠ `git log -S` is BANNED as the primary method here. Demonstration of WHY,
reproduced at HEAD -- note that it prints rows to stdout AND returns rc=128:

`$ git log -S 'bf16289' --oneline --no-decorate -- .planning/HANDOFF.json`

```
fatal: unable to read 8c3b13dbfd13070afe1223c5e34b096b38f4c92d
f78631c docs(quick-260806-sr4): freeze rescoped bytes->CODE; K-3 closed; a false handoff claim retracted
2bda675 docs(handoff): 2026-08-03 close-session — m3-04b landed; AFR_aou panel is UNREACHABLE, do not fire
```
rc=128

That is a TRUNCATED list with a plausible shape. `git log` walks
newest->oldest, so what a missing blob cuts off is exactly the OLD end --
which is exactly where a "when did the frozen label first attach?" answer
lives. The loop below reads every revision and reports what it could not read.

### OBJECT-STORE CENSUS

Every revision of every narrative file was ATTEMPTED. Revisions whose blob
could not be read are listed by SHA below, never silently skipped. Because
the unreadable set skews OLD, every first-appearance date in this document
is a **LOWER BOUND**.

#### `.planning/HANDOFF.json`

```
total_revisions=76 readable=59 unreadable=17
```

UNREADABLE commit SHAs for `.planning/HANDOFF.json` (count=17):

```
2919a392ad45f2e2da314b7002d4b258b5b1e0a0
889f692257b8831c244a538a70f334e250abad28
49cb50f0cb2d95f7fd03ed12a079c0a4d28ec3a9
66c1931d806320c8c5415e2f58c03ee001963d7d
6c1c27b7295457afcf75237504f3f7bf8f891088
f159b158f15e2f34537477e7512c9035253e9aab
d82b9e4a3201b6c817862637eed216b9a5832fd1
997461b362b83b9b35b03f699de6cccf1429a46a
f67ac19fc015e035a665a54f77181be9696e90cc
603482dd06deecdbc3e4cfaa64e51d37f451321d
8445850552089b690040c42a149ea0b02cdc1ce4
b82986227a8f968edd62676d127e05c70bbc1059
c89008ce74a1ff46afae613358d9f5714e440f7f
9646ac98a901c04cb52a52a77e9193b2764c9a54
3dd05a2baaa50752ebe2f023656f057578b4c8f4
a83f1c2c588c328df956166e64e7d5bdb74a5cf9
5c2f0904498663647d176b5f28b979edaa4c0acb
```

Earliest READABLE revision of `.planning/HANDOFF.json` in which each basename appears on a
line that also carries a freeze word (`frozen|freeze|pinned|pin`):

```
occlusion_manifest.py: 10 readable revisions; earliest = 217b354 2026-07-15 docs(handoff): 2026-07-15 close-session — m3-07b LANDED (span-filter + manifest are real code); PAUSED before 07c; ONE test-vs-test contradiction awaiting a Carter call
occlusion_present_rate_scan.py: 15 readable revisions; earliest = e3075ae 2026-07-15 test(quick-260715-sqe): UAT 14/14 automated + record blast-radius findings
drop_occluded_from_sumstats.py: 11 readable revisions; earliest = 4070dd9 2026-07-16 docs(m3-07c): m3-07 is CODE-COMPLETE — 07c landed, suite has no reds
ld_npz_to_rds.R: 22 readable revisions; earliest = 262ff12 2026-06-19 docs(handoff): close session — m3-02b executed + reviewed + CR-01/warnings fixed + blast-radius swept (BR-01 caught); next = m3-02c
pipeline.schema.yaml: 5 readable revisions; earliest = 63453db 2026-08-06 docs(handoff): 2026-08-06 close — blast radius REMEDIATED; all gate rows clear but one
COLLECTIVE-pinned-files: 12 readable revisions; earliest = 2bda675 2026-08-03 docs(handoff): 2026-08-03 close-session — m3-04b landed; AFR_aou panel is UNREACHABLE, do not fire
COLLECTIVE-7-pinned-files: 12 readable revisions; earliest = 2bda675 2026-08-03 docs(handoff): 2026-08-03 close-session — m3-04b landed; AFR_aou panel is UNREACHABLE, do not fire
```

#### `.planning/STATE.md`

```
total_revisions=304 readable=275 unreadable=29
```

UNREADABLE commit SHAs for `.planning/STATE.md` (count=29):

```
bde00ee6aa416a3a97a410f9b0483753cd7b0573
969f6e56d52b45fc6034d642cbc0ba93a607cd24
2919a392ad45f2e2da314b7002d4b258b5b1e0a0
889f692257b8831c244a538a70f334e250abad28
49cb50f0cb2d95f7fd03ed12a079c0a4d28ec3a9
66c1931d806320c8c5415e2f58c03ee001963d7d
6c1c27b7295457afcf75237504f3f7bf8f891088
f159b158f15e2f34537477e7512c9035253e9aab
fdf257c4ed97c4e34c44acdc34cc2687040d5566
fcfbc74ff94ef77de02869a524a9bb089b6df30e
d82b9e4a3201b6c817862637eed216b9a5832fd1
997461b362b83b9b35b03f699de6cccf1429a46a
07edafcea709b135eb451c2670d788e2dbdafa4f
202ec4d95f2ee48b4064b84ffa396a3d7523ba6f
603482dd06deecdbc3e4cfaa64e51d37f451321d
8445850552089b690040c42a149ea0b02cdc1ce4
b82986227a8f968edd62676d127e05c70bbc1059
e0f41823efe77ec11f7228304a8b648f38292c71
c89008ce74a1ff46afae613358d9f5714e440f7f
9646ac98a901c04cb52a52a77e9193b2764c9a54
48da268e95d0dc2076f60444a9b64fb5064cf2fd
a95b86c6f90dadf4a72840fa0f1c3e449f9a65ca
dafb2c50069f94806e6f8e4399a77d07cb0b6900
012abb1e73fc419c94101d6152f1a0bd6b9824f4
5c2f0904498663647d176b5f28b979edaa4c0acb
e019400ceab21d273260892e122083725ee0c5d6
e38e8f250ea911b4a710ff1bfc78a3539566942e
421e3e7c11509ae56c2b749f94a39d6acca3c463
7e165dd8172df3cd7cb0d6eb99d3c3ae88bf00a8
```

Earliest READABLE revision of `.planning/STATE.md` in which each basename appears on a
line that also carries a freeze word (`frozen|freeze|pinned|pin`):

```
occlusion_manifest.py: 26 readable revisions; earliest = bd3fe0e 2026-07-15 docs(m3-07a): complete Wave 0 — SUMMARY + STATE (RED landed 296157a, tag m3-07a-W7-T-WAVE0; PAUSE before 07b/07c)
occlusion_present_rate_scan.py: 26 readable revisions; earliest = bd3fe0e 2026-07-15 docs(m3-07a): complete Wave 0 — SUMMARY + STATE (RED landed 296157a, tag m3-07a-W7-T-WAVE0; PAUSE before 07b/07c)
drop_occluded_from_sumstats.py: 26 readable revisions; earliest = bd3fe0e 2026-07-15 docs(m3-07a): complete Wave 0 — SUMMARY + STATE (RED landed 296157a, tag m3-07a-W7-T-WAVE0; PAUSE before 07b/07c)
ld_npz_to_rds.R: 84 readable revisions; earliest = 262ff12 2026-06-19 docs(handoff): close session — m3-02b executed + reviewed + CR-01/warnings fixed + blast-radius swept (BR-01 caught); next = m3-02c
pipeline.schema.yaml: 3 readable revisions; earliest = f78631c 2026-08-06 docs(quick-260806-sr4): freeze rescoped bytes->CODE; K-3 closed; a false handoff claim retracted
COLLECTIVE-pinned-files: 14 readable revisions; earliest = 2bda675 2026-08-03 docs(handoff): 2026-08-03 close-session — m3-04b landed; AFR_aou panel is UNREACHABLE, do not fire
COLLECTIVE-7-pinned-files: 14 readable revisions; earliest = 2bda675 2026-08-03 docs(handoff): 2026-08-03 close-session — m3-04b landed; AFR_aou panel is UNREACHABLE, do not fire
```

#### `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md`

```
total_revisions=64 readable=42 unreadable=22
```

UNREADABLE commit SHAs for `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` (count=22):

```
b128dba0c797e4b76d387653ada211e41dd3f323
bde00ee6aa416a3a97a410f9b0483753cd7b0573
3a7d7b73c8e425458969c8842ec115955f1ccb6a
2919a392ad45f2e2da314b7002d4b258b5b1e0a0
49cb50f0cb2d95f7fd03ed12a079c0a4d28ec3a9
f159b158f15e2f34537477e7512c9035253e9aab
fcfbc74ff94ef77de02869a524a9bb089b6df30e
d82b9e4a3201b6c817862637eed216b9a5832fd1
997461b362b83b9b35b03f699de6cccf1429a46a
0667976980791b41ac309e46d293f3dae394c689
31a1809a7a18371bad90de743f8af68f0d303348
0e3ef2acd0d3018b4d0db4874b7886e7069b2d6b
07edafcea709b135eb451c2670d788e2dbdafa4f
9f0c837dfa9def293d0b821b5fb1274a3795bd3b
603482dd06deecdbc3e4cfaa64e51d37f451321d
8445850552089b690040c42a149ea0b02cdc1ce4
b82986227a8f968edd62676d127e05c70bbc1059
c89008ce74a1ff46afae613358d9f5714e440f7f
9646ac98a901c04cb52a52a77e9193b2764c9a54
3dd05a2baaa50752ebe2f023656f057578b4c8f4
a83f1c2c588c328df956166e64e7d5bdb74a5cf9
5c2f0904498663647d176b5f28b979edaa4c0acb
```

Earliest READABLE revision of `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` in which each basename appears on a
line that also carries a freeze word (`frozen|freeze|pinned|pin`):

```
occlusion_manifest.py: 11 readable revisions; earliest = 217b354 2026-07-15 docs(handoff): 2026-07-15 close-session — m3-07b LANDED (span-filter + manifest are real code); PAUSED before 07c; ONE test-vs-test contradiction awaiting a Carter call
occlusion_present_rate_scan.py: 10 readable revisions; earliest = bf16289 2026-07-16 docs(handoff): 2026-07-16 close-session — m3-07 CODE-COMPLETE; unambiguous resume point
drop_occluded_from_sumstats.py: 10 readable revisions; earliest = bf16289 2026-07-16 docs(handoff): 2026-07-16 close-session — m3-07 CODE-COMPLETE; unambiguous resume point
ld_npz_to_rds.R: 14 readable revisions; earliest = bd4d50a 2026-07-07 docs(handoff): 2026-07-07 close-session — m3-06 HELD (NaN mechanism RESOLVED = overlapping-deletion occlusion); verdict-commit pending base64; loop-state + 3 policy calls on Carter
pipeline.schema.yaml: 9 readable revisions; earliest = 2bda675 2026-08-03 docs(handoff): 2026-08-03 close-session — m3-04b landed; AFR_aou panel is UNREACHABLE, do not fire
COLLECTIVE-pinned-files: 9 readable revisions; earliest = 2bda675 2026-08-03 docs(handoff): 2026-08-03 close-session — m3-04b landed; AFR_aou panel is UNREACHABLE, do not fire
COLLECTIVE-7-pinned-files: 9 readable revisions; earliest = 2bda675 2026-08-03 docs(handoff): 2026-08-03 close-session — m3-04b landed; AFR_aou panel is UNREACHABLE, do not fire
```

#### CENSUS TOTALS

```
unreadable=17 .planning/HANDOFF.json
unreadable=29 .planning/STATE.md
unreadable=22 .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
```
### ⚠ D1 — STEP 5a CORRECTED: the entry extraction above returned EMPTY

The awk in the previous block anchored on `^## DEC-2026-08-06-sr4-freeze-scope`,
but the actual heading (line 1039) is `## 2026-08-06 — DEC-2026-08-06-sr4-freeze-scope: ...`.
It therefore matched nothing and printed an EMPTY fenced block with **rc=0** --
a silent empty result wearing a success code. Recorded rather than quietly
overwritten. The corrected extraction:

`$ sed -n '1039,1075p' .planning/DECISIONS.md`

```
## 2026-08-06 — DEC-2026-08-06-sr4-freeze-scope: the source freeze is a CODE pin, not a byte pin; comments are deliberately FREE

**Decision:** The **source-file** freeze in this repository pins **CODE**, not
bytes. Comments, Python docstrings, blank lines and trailing whitespace are
**deliberately outside** every freeze gate. Landed by `quick-260806-sr4` under
`AUTH-SR4-RESCOPE`, `AUTH-SR4-K3` and `AUTH-SR4-EXTEND` (Carter, 2026-08-06).

**What is pinned:**

- The **CODE** of `src/legacy/region_analysis/scripts/run_susie_rss.R` at
  `bf04199` — a whole-file code-only **floor** plus five named numeric-bearing
  symbols (`regularize_ld`, `run_susie_with_ladder`, `safe_region_id`,
  `load_ld_matrix`, `assert_declared_ld_authoritative`). The symbol pins are
  **diagnostics** (they name *which* block moved); **the floor is the safety
  net**, and it is not optional: `:659-1357` — roughly 700 lines including the
  fitting flow and all three `toJSON` emits — lives inside **no function at
  all**.
- The **CODE** of `src/python/plink_ld_to_npz.py`,
  `src/python/condition_ld_matrix.py` and `src/python/occlusion_span_filter.py`
  at `bf16289` — whole-file plus all **22** top-level symbols (13 + 3 + 6),
  **derived from the source at the pin, never hand-transcribed**. Before this,
  `bf16289` was enforced by **zero** tests anywhere in the repository.

**What is deliberately FREE:** comments, docstrings, blank lines, trailing
whitespace. **Fixing a wrong comment in a frozen file now costs nothing** — no
unfreeze, no re-pin, no decision.

**Why a guard exists at all:** `BLOCKER-1` proved this pipeline can move Track A
numbers **silently** — fixing the LD read path moved EUR `r[1,2]` 0.1 → 0.9,
credible sets 3 → 10, nonzero PIPs 200 → 78, while `ld_status` and
`ld_overlap_fraction` (the two fields anyone would check to argue nothing moved)
stayed **byte-identical**. And there is no cheap regression oracle: re-checking
the AFR side needs the AoU perimeter and the ~11-day billed fire. **Silent
numeric drift with no cheap oracle is the threat.** The guard is not weakened
here; it is aimed at the right target.

**Context — the cost of the old scope was concrete.** The byte pin
```
rc=0

The "What is pinned" region of the same entry, and its SR4-OPEN registration:

`$ sed -n '1050,1075p' .planning/DECISIONS.md`

```
  symbols (`regularize_ld`, `run_susie_with_ladder`, `safe_region_id`,
  `load_ld_matrix`, `assert_declared_ld_authoritative`). The symbol pins are
  **diagnostics** (they name *which* block moved); **the floor is the safety
  net**, and it is not optional: `:659-1357` — roughly 700 lines including the
  fitting flow and all three `toJSON` emits — lives inside **no function at
  all**.
- The **CODE** of `src/python/plink_ld_to_npz.py`,
  `src/python/condition_ld_matrix.py` and `src/python/occlusion_span_filter.py`
  at `bf16289` — whole-file plus all **22** top-level symbols (13 + 3 + 6),
  **derived from the source at the pin, never hand-transcribed**. Before this,
  `bf16289` was enforced by **zero** tests anywhere in the repository.

**What is deliberately FREE:** comments, docstrings, blank lines, trailing
whitespace. **Fixing a wrong comment in a frozen file now costs nothing** — no
unfreeze, no re-pin, no decision.

**Why a guard exists at all:** `BLOCKER-1` proved this pipeline can move Track A
numbers **silently** — fixing the LD read path moved EUR `r[1,2]` 0.1 → 0.9,
credible sets 3 → 10, nonzero PIPs 200 → 78, while `ld_status` and
`ld_overlap_fraction` (the two fields anyone would check to argue nothing moved)
stayed **byte-identical**. And there is no cheap regression oracle: re-checking
the AFR side needs the AoU perimeter and the ~11-day billed fire. **Silent
numeric drift with no cheap oracle is the threat.** The guard is not weakened
here; it is aimed at the right target.

**Context — the cost of the old scope was concrete.** The byte pin
```
rc=0

`$ sed -n '1150,1170p' .planning/DECISIONS.md`

```
  `_strip_py_comments`, `_strip_r_comments`, `_code_only`, `_strip_comments`,
  `_strip_hash_comments`), and `_code_lines` in
  `test_variant_catalog_fallback_legacy_semantics.py` is a hand-rolled instance
  of this very utility. They are **registered and superseded going forward**;
  **none is refactored**, because each backs a different assertion with
  deliberate semantics (`strip_py_comments` KEEPS triple-quoted strings because a
  Snakemake `shell:` body IS one; `code_only` DELETES them) and rewiring them is
  unauthorized and carries real regression risk. `r_code_only` is deliberately
  **kept** and consumed as an **independent R cross-check** of the new mask.
  What existed **nowhere** was the **FREEZE convention** itself — no
  `DECISIONS.md` entry, and `bf16289` enforced by zero tests.
- **What this does NOT cover, stated as a limit rather than sold as coverage:**
  the pins are over **source text** only. They detect *that code moved*, never
  *whether a number moved*. No fit is run and no `.rds`, `.npz` or region JSON is
  produced or compared. YAML support was deliberately **not** built.
- Cross-refs: `[[feedback_extract_reusable_utilities]]`,
  `[[feedback_fixed_sha_whole_file_pin_is_a_timebomb]]`,
  `[[feedback_green_assertion_needs_a_negative_control]]`,
  `[[feedback_negative_control_defeated_by_bytecode_cache]]`,
  `[[feedback_fixing_a_split_unpins_what_it_pinned]]`; K-3 in
  `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`;
```
rc=0

Does the entry name ANY of the five? (measured, per basename, within the entry)

`$ awk 'NR>=1039 && NR<=1250' .planning/DECISIONS.md > /tmp/pmv_dec_entry.txt; wc -l /tmp/pmv_dec_entry.txt`

```
212 /tmp/pmv_dec_entry.txt
```
rc=0

`$ grep -c 'occlusion_manifest.py' /tmp/pmv_dec_entry.txt`

```
0
```
rc=1

`$ grep -c 'occlusion_present_rate_scan.py' /tmp/pmv_dec_entry.txt`

```
0
```
rc=1

`$ grep -c 'drop_occluded_from_sumstats.py' /tmp/pmv_dec_entry.txt`

```
0
```
rc=1

`$ grep -c 'ld_npz_to_rds.R' /tmp/pmv_dec_entry.txt`

```
0
```
rc=1

`$ grep -c 'pipeline.schema.yaml' /tmp/pmv_dec_entry.txt`

```
0
```
rc=1

`$ grep -n 'MOVED\|moved\|five' /tmp/pmv_dec_entry.txt | head -20`

```
11:  `bf04199` — a whole-file code-only **floor** plus five named numeric-bearing
14:  **diagnostics** (they name *which* block moved); **the floor is the safety
29:numbers **silently** — fixing the LD read path moved EUR `r[1,2]` 0.1 → 0.9,
31:`ld_overlap_fraction` (the two fields anyone would check to argue nothing moved)
66:  argued:** perturbing the `:1357` emit goes RED on the floor while all five
75:  demonstrably moved** and declaring a moving file frozen is a **decision**, not
124:  the pins are over **source text** only. They detect *that code moved*, never
125:  *whether a number moved*. No fit is run and no `.rds`, `.npz` or region JSON is
157:Across the **five regions Track A's coloc numbers actually depend on**:
193:   by this decision: is this a LIMITATION or a CORRECTION?** Two of five coloc
```
rc=0

### D2 — the TEXT of the earliest matching narrative lines

A basename co-occurring with a freeze word ON A LINE is a LOOSE criterion --
it over-matches, which is the conservative direction for a "was it EVER
declared frozen?" question (it makes a hit easier, so a null is stronger).
But it means the hits must be READ, not counted. Here they are.

**`occlusion_manifest.py` @ `.planning/HANDOFF.json` @ earliest readable rev `217b354`:**

`$ git show '217b354:.planning/HANDOFF.json' | grep -i -- 'occlusion_manifest.py' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
  "blast_radius_findings": "3 parallel read-only investigators swept the 07a RED. The change touched ZERO production code (all frozen contracts 0-line diff), so the real downstream consumer was 07b's IMPLEMENTATION — and the CONTRACT was defective. BLOCKER: test_occlusion_manifest.py demanded snpC (5922718) be occlusion_order=='second_order', INVERTING the byte-verified verdict (pair 3 DEL 5922716
```
rc=0

**`occlusion_present_rate_scan.py` @ `.planning/HANDOFF.json` @ earliest readable rev `e3075ae`:**

`$ git show 'e3075ae:.planning/HANDOFF.json' | grep -i -- 'occlusion_present_rate_scan.py' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
    "⛔ NEW BLOCKER FOR 07c — FOUND 2026-07-15 by a 4-agent /assess-blast-radius sweep, BEFORE 07c was built. FIX THE RED BEFORE EXECUTING 07c. The scan→enrich SEAM key types DISAGREE and the mismatch fails SILENTLY. Producer RED (07c, unbuilt): tests/m3/test_occlusion_present_rate_scan.py:79-84 pins `scan_present_rate` to return a dict keyed by a (chr, pos) TUPLE on GRCh37 (`target = (1, 5_982_778
```
rc=0

**`drop_occluded_from_sumstats.py` @ `.planning/HANDOFF.json` @ earliest readable rev `4070dd9`:**

`$ git show '4070dd9:.planning/HANDOFF.json' | grep -i -- 'drop_occluded_from_sumstats.py' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
    "✅ m3-07c — EXECUTED AND COMPLETE 2026-07-16 (c475da7 T3 + ed3e122 T4; Carter authorized it with 'Proceed' in direct response to 'your explicit go is the only thing gating it'). Built GREEN against the 07a REDs, which are UNEDITED (tests/ 0-line diff — no test was touched to force green). T3 = src/python/occlusion_present_rate_scan.py (scan_present_rate, 6 RED → 6 passed); T4 = src/python/drop
```
rc=0

**`ld_npz_to_rds.R` @ `.planning/HANDOFF.json` @ earliest readable rev `262ff12`:**

`$ git show '262ff12:.planning/HANDOFF.json' | grep -i -- 'ld_npz_to_rds.R' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
    "executed": "m3-02b-W2-rescope-split-stitch-code (Wave 0, autonomous) — 3 TDD tasks: (1) overlapping-window xlarge split in build_ld_region_manifest.py (half-open cores tile parent + core+/-buffer windows + explicit buffer_bp) + dev tuple-resolve/capped-expansion + AF metadata in aou_ld_panel.py .npz; (2) NEW stitch_subregions_to_rds.R BANDED sparse stitch (cross-core pairs within buffer_bp re
```
rc=0

**`pipeline.schema.yaml` @ `.planning/HANDOFF.json` @ earliest readable rev `63453db`:**

`$ git show '63453db:.planning/HANDOFF.json' | grep -i -- 'pipeline.schema.yaml' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
  "freeze_state": "run_susie_rss.R RE-FROZEN at dc4bbd2 — the 2026-08-05 unfreeze is SPENT and does NOT carry over; b77 did NOT unfreeze it (its differential test READS it via a body-walk extractor). Six frozen Python modules + src/snakemake/schemas/pipeline.schema.yaml all 0-diff. m3-06 stays HELD (no NaN->0, no condition_ld_matrix.py). run_finemap.params.region_id byte-unchanged, guarded by BOTH
```
rc=0

**`occlusion_manifest.py` @ `.planning/STATE.md` @ earliest readable rev `bd3fe0e`:**

`$ git show 'bd3fe0e:.planning/STATE.md' | grep -i -- 'occlusion_manifest.py' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
> **⛔ NEXT = PAUSE. 07b/07c are UNBLOCKED but NOT AUTHORIZED** — Carter's standing instruction is "07a then PAUSE". 07b = production code (`occlusion_span_filter.py`, `--exclude` wiring in `run_native_ld_panel.py` + `aou_ld_panel.py`, `_PANEL_COLUMNS` += `n_dropped_occluded`); 07c = `occlusion_manifest.py` + `occlusion_present_rate_scan.py` + `drop_occluded_from_sumstats.py`. Both await Carter's e
```
rc=0

**`ld_npz_to_rds.R` @ `.planning/STATE.md` @ earliest readable rev `262ff12`:**

`$ git show '262ff12:.planning/STATE.md' | grep -i -- 'ld_npz_to_rds.R' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
- **Executed `m3-02b`** (`/gsd-execute-phase m3` scoped to m3-02b) — 3 TDD tasks: (1) overlapping-window xlarge split in `build_ld_region_manifest.py` (half-open cores tile parent + core±buffer windows + explicit `buffer_bp`) + dev tuple-resolve/capped-expansion + AF metadata in `aou_ld_panel.py` `.npz`; (2) **NEW** `stitch_subregions_to_rds.R` BANDED sparse stitch (cross-core pairs within `buffer
```
rc=0

**`pipeline.schema.yaml` @ `.planning/STATE.md` @ earliest readable rev `f78631c`:**

`$ git show 'f78631c:.planning/STATE.md' | grep -i -- 'pipeline.schema.yaml' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
Last activity: 2026-08-06 (latest) - Completed quick task **260806-sr4** — **the source freeze is RESCOPED from BYTES to CODE, and K-3 is CLOSED as the acceptance proof**. Commits `98e0ee9`/`656529a`/`c04e672`/`5f0520b`. **BOTH suites independently re-run by the orchestrator: `tests/m3` 902 passed / 31 skipped / 0 failed (baseline 822, +80) and `tests/phase2` 136 / 1 / 0** — skips unchanged at 31 
```
rc=0

**`occlusion_manifest.py` @ `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` @ earliest readable rev `217b354`:**

`$ git show '217b354:.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md' | grep -i -- 'occlusion_manifest.py' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
> **m3-07b LANDED** (`7734725`/T1 + tag `m3-07b-W7-T1`; `0473b6a`/T2 + tag `m3-07b-W7-T2`; `a76ebe5` docs). NEW: `src/python/occlusion_span_filter.py`, `src/python/occlusion_manifest.py`. MODIFIED: `aou_ld_panel.py` (`build_plink_ld_command(exclude=)`) + `run_native_ld_panel.py` (`process_region` reorder — raw-window read + filter BEFORE plink, `--exclude` before `--r` — plus the `n_dropped_occlud
```
rc=0

**`occlusion_present_rate_scan.py` @ `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` @ earliest readable rev `bf16289`:**

`$ git show 'bf16289:.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md' | grep -i -- 'occlusion_present_rate_scan.py' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
> **★ m3-07c LANDED** (`c475da7` T3 + `ed3e122` T4) — authorized by Carter's **"Proceed"** in direct reply to *"your explicit go is the only thing gating it."* NEW: `src/python/occlusion_present_rate_scan.py` (`scan_present_rate`; 6 RED → **6 passed**) + `src/python/drop_occluded_from_sumstats.py` (`drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict`, **file-in/file-out**;
```
rc=0

**`drop_occluded_from_sumstats.py` @ `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` @ earliest readable rev `bf16289`:**

`$ git show 'bf16289:.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md' | grep -i -- 'drop_occluded_from_sumstats.py' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
> **★ m3-07c LANDED** (`c475da7` T3 + `ed3e122` T4) — authorized by Carter's **"Proceed"** in direct reply to *"your explicit go is the only thing gating it."* NEW: `src/python/occlusion_present_rate_scan.py` (`scan_present_rate`; 6 RED → **6 passed**) + `src/python/drop_occluded_from_sumstats.py` (`drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict`, **file-in/file-out**;
```
rc=0

**`ld_npz_to_rds.R` @ `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` @ earliest readable rev `bd4d50a`:**

`$ git show 'bd4d50a:.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md' | grep -i -- 'ld_npz_to_rds.R' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
> **(A)** m3-06-W6-ld-nan-psd-conditioning (999.1 §2-4) LANDED via autonomous plan→execute per Carter's `--auto --chain`, structured as a WAVE-in-m3 (his call, not a standalone phase): promote `20e3adc` → planner `205b03e` → plan-checker PASS → executor 6 commits HEAD `f147041` (`psd_utils.R` byte-identical r3 refactor 16/16 `identical()` → Track-A numerics UNCHANGED; `condition_ld_matrix.py`; `wr
```
rc=0

**`pipeline.schema.yaml` @ `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` @ earliest readable rev `2bda675`:**

`$ git show '2bda675:.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md' | grep -i -- 'pipeline.schema.yaml' | grep -iE 'frozen|freeze|pinned|pin' | cut -c1-400 | head -3`

```
> **⚠ Plan wrong twice (both fixed):** `envs/m3-r-ld.yml` lacked pandas (added `pandas>=2.2` there, NOT to `python_stats.yml` which backs a dozen built rules); `pipeline.schema.yaml` is `additionalProperties:false` so the new `occlusion_lockstep:` block needed a schema entry or every Snakemake run dies at `validate()`. **⚠ One existing test edited** — `test_production_boundary_documented` REPLACED
```
rc=0

#### The COLLECTIVE phrase, at its earliest readable appearance

`$ git show '2bda675:.planning/HANDOFF.json' | grep -iE '7 pinned files' | cut -c1-400`

```
    "All 7 pinned files 0-line diff vs bf16289: the 4 m3-07 modules (occlusion_span_filter, occlusion_manifest, occlusion_present_rate_scan, drop_occluded_from_sumstats) + the 3 frozen contracts (plink_ld_to_npz.py, ld_npz_to_rds.R, condition_ld_matrix.py).",
    "m3_04b": "✅ COMPLETE 2026-08-03. Both tasks landed; tests/m3 444P/31S/0F independently re-verified by the orchestrator; all 7 pinned files 0-line diff.",
```
rc=0

`$ git show '2bda675:.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md' | grep -iE '7 pinned files' | cut -c1-400`

```
> **★ m3-04b LANDED** (`d7dfa67` T1 + `0cae502`/`37c51df` T2 + `f038ce0` docs). T1 = `assemble_occlusion_catalog.py`, the FIRST production caller for the four zero-caller m3-07 functions. T2 = the lockstep seam (`occlusion_lockstep_cli.py` + `m3_occlusion_lockstep.smk`) wiring BOTH `run_finemap.input.sumstats` AND `input.variants`, AFR-gated so EUR/Track-A strings stay byte-identical. **`tests/m3`
```
rc=0

#### What `bf16289` -- the pin itself -- SAYS about a freeze, in the one file it touched

`$ git show 'bf16289:.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md' | grep -inE 'frozen|freeze|pinned' | cut -c1-400 | head -20`

```
15:> **★ m3-07c LANDED** (`c475da7` T3 + `ed3e122` T4) — authorized by Carter's **"Proceed"** in direct reply to *"your explicit go is the only thing gating it."* NEW: `src/python/occlusion_present_rate_scan.py` (`scan_present_rate`; 6 RED → **6 passed**) + `src/python/drop_occluded_from_sumstats.py` (`drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict`, **file-in/file-out
31:> **m3-07b LANDED** (`7734725`/T1 + tag `m3-07b-W7-T1`; `0473b6a`/T2 + tag `m3-07b-W7-T2`; `a76ebe5` docs). NEW: `src/python/occlusion_span_filter.py`, `src/python/occlusion_manifest.py`. MODIFIED: `aou_ld_panel.py` (`build_plink_ld_command(exclude=)`) + `run_native_ld_panel.py` (`process_region` reorder — raw-window read + filter BEFORE plink, `--exclude` before `--r` — plus the `n_dropped_occ
44:> **Nothing running NC-State; $0.** `/gsd-plan-phase m3-07 --auto --chain` ran to completion: research `a795fac` (#1 crux resolved — panel `.bim` A2 carries the full multi-char indel REF, so a deletion span `[POS, POS+len(A2)−1]` is computable from the window `.bim` alone; no new data plumbing) → validation `7f701a8` → plan v1 `7272d03` → **checker-split into 3 plans** `0d3e37e` → gsd-plan-chec
47:> **Nothing running server-side, $0. Local HEAD `8f36fdf` = 2 commits AHEAD of origin `bd4d50a`, HELD unpushed ON PURPOSE (Carter order = hold-then-push-all-four).** THIS SESSION (docs-only, read-only, no perimeter): ran Seth's exclude-vs-flag **hinge check** — the panel↔sumstats join is `(CHR,POS)`-only (`snp_id_bridge.R`), panel GRCh38 / sumstats GRCh37 (`ld_npz_to_rds.R` liftover); lifted th
50:> **(A)** m3-06-W6-ld-nan-psd-conditioning (999.1 §2-4) LANDED via autonomous plan→execute per Carter's `--auto --chain`, structured as a WAVE-in-m3 (his call, not a standalone phase): promote `20e3adc` → planner `205b03e` → plan-checker PASS → executor 6 commits HEAD `f147041` (`psd_utils.R` byte-identical r3 refactor 16/16 `identical()` → Track-A numerics UNCHANGED; `condition_ld_matrix.py`; 
161:> **2026-06-11 PM (wb CLI + cluster LIVE — SUPERSEDED: cluster STOPPED 2026-06-12, see LATEST above):** Verily Workbench `wb` CLI installed + authed on the NCSU HPC node (wrappers `~/bin/wb` + `~/bin/gcloud`; full setup + capability map in memory `reference_wb_cli_hpc_setup`). **Capability boundary established empirically:** control-plane works off-perimeter (workspace/resource list+describe, 
```
rc=0

#### And the diff `bf16289` actually landed

`$ git show bf16289 --format='' | head -60`

```
diff --git a/.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md b/.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
index 154a6e1..cdbc00c 100644
--- a/.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
+++ b/.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
@@ -8,7 +8,23 @@ status: cohort_banked_gate15_complete_durablefix_phase2_item1_landed_gate1cost_a
 last_updated: 2026-06-11T15:30:00.000Z
 ---
 
-> **2026-07-15 (★ LATEST ★ — SESSION CLOSE: m3-07a COMPLETE+VERIFIED and m3-07b LANDED; the occlusion span-filter + provenance manifest are REAL CODE; PAUSED before 07c; ⚠ ONE test-vs-test contradiction awaiting a Carter call):**
+> **2026-07-16 (★ LATEST ★ — SESSION CLOSE: ★ m3-07 IS CODE-COMPLETE — 07c EXECUTED on Carter's go; full `tests/m3` = 0 failed / 420 passed / 31 skipped, NO REDS AT ALL for the first time in this wave):**
+>
+> **Nothing running. $0. NO perimeter contact this entire session** (everything NC-State, code-only). `origin == local == e9be72e`; remote is SSH (no PAT). No AoU fire, no cluster, no orphan jobs — one stray background waiter of mine was found and killed at close.
+>
+> **★ m3-07c LANDED** (`c475da7` T3 + `ed3e122` T4) — authorized by Carter's **"Proceed"** in direct reply to *"your explicit go is the only thing gating it."* NEW: `src/python/occlusion_present_rate_scan.py` (`scan_present_rate`; 6 RED → **6 passed**) + `src/python/drop_occluded_from_sumstats.py` (`drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict`, **file-in/file-out**; 9 RED → **9 passed**). Built GREEN against the 07a REDs — **`tests/` 0-line diff: no test was edited to force green.** Full `tests/m3` **15F/405P/31S → 0F/420P/31S**. `finemap.smk` UNTOUCHED (**m3-04 consume-wiring stays a DISCLOSED deferral**). Frozen contracts 0-line diff ALL session; neither new module references `condition_ld_matrix`/`nan_to_num` (**m3-06 stays HELD**). **The real 9-file genome-wide scan was NOT run** — GATED INTEGRATION step, needs the perimeter.
+>
+> **⚠ THE ONE THING GREEN TESTS COULD NOT PROVE:** the RED does **not** pin T3's key **canonicalization**. The real producer emits `chr` as the **string `'1'`**; the RED keys on the **int `1`**. Echoing the caller's tuple back verbatim **passes all 6 tests** and would have made `enrich_occlusion_manifest` match **ZERO** liftable rows (the `63bdb59` guard would then have RAISED at integration — defense-in-depth working, but still a build-time bug). T3 canonicalizes on both paths; re-proved end-to-end: `scan_present_rate([('1', 5982778)])` → keys `[(1, 5982778)]` → feedable to `enrich_occlusion_manifest(present_rate=)`; record `{n_traits_present: 2, n_traits_scanned: 3, present_rate: 2/3}`.
+>
+> **FOUR PRE-EXISTING DEFECTS ALSO CLOSED** (none caused by the resume; `src/` untouched by it): **panel-column test-vs-test contradiction** `957d5a1` (UAT 14/14; the 07a RED preserved, verified PASSED-not-skipped; the call was made by the AGENT on byte-verified precedent `1a9d170`, **not** a Carter ruling — revertible in 1 line); **the scan→enrich seam key contract that BLOCKED 07c** `63bdb59` (the 07a RED was **RIGHT**, the SHIPPED 07b consumer was **WRONG**; found by a 4-agent `/assess-blast-radius` sweep **BEFORE** 07c was built — it would have silently blanked the rs182965575 "present in 7/9" evidence across all 276 regions with both suites green); **panel-TSV header guard** `fe375e7`; **P3** `ff8cc47` — the gsutil-blip bucket overwrite that would have **silently** destroyed banked provenance mid-fire (root cause: ONE helper serving TWO callers with **opposite** failure-safety requirements → see [[feedback_failsafe_default_is_caller_relative]]). Plus the **07c PLAN reconciliation** `8d4087a` — the handoff's *"07c's plan has no drift"* was **STALE AND WRONG for BOTH tasks**; T4 slipped a **name-only** check. **Rule baked: GREP THE NAME, THEN READ THE ASSERTIONS.**
+>
+> **⚠ TWO FLAGGED, NOT ACTIONED** (pre-existing `63bdb59` consumer behaviour — decide when the Angle-1/3 catalog lands): `present_rate` is never persisted as a manifest column (derivable as k/n), and `traits_present` **serializes as a stringified list** (`"['bmi','ldl']"`) so a catalog reader gets a `str`, not a `list`.
+>
+> **NEXT = the loop re-fire arc. ALL CARTER'S; ALL need the AoU perimeter (NOT reachable from NC-State):** (1) **OPERATIONAL** — rotate/delete the stale `gs://` panel TSV BEFORE firing: `gsutil stat <panel-uri>`; if present, `gsutil cat <uri> | head -1 | tr '\t' '\n' | wc -l` must be **9**, else `gsutil rm`. ⚠ **"0/276 banked" is measured in `.npz` and does NOT evidence its absence** — the `.npz` (not the TSV) gate the resume skip, and the June/July fires appended `status=error` rows unconditionally at `:808` on 7-col (Jun 28-30) and 8-col (Jul-02 `2d23d67`) code. Zero risk (only error rows = no data value), zero compute cost. (2) The **gated real-`.bim` validation** — ⚠ open **0- vs 1-based index-origin** question on `_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES`. (3) A **region-1 re-run** must validate. (4) The **~11-day billed fire** (Carter's trigger; liveness = the GCS `.npz` listing climbing to **276** — NOT the kernel light, NOT `_SUCCESS`). AoU VM **STOPPED-not-deleted** (holds `/home/jupyter/afr_cohort`); `.npz` **0/276**.
+>
+> **Resume = `.planning/HANDOFF.json` (2026-07-16T01:00Z) + `.planning/STATE.md` 2026-07-16 block + this block.** **SUPERSEDES the 2026-07-15 block below.**
+
+> **2026-07-15 (SUPERSEDED by the 2026-07-16 block above — m3-07a COMPLETE+VERIFIED and m3-07b LANDED; the occlusion span-filter + provenance manifest are REAL CODE; PAUSED before 07c; the test-vs-test contradiction it flags is now RESOLVED via `957d5a1`):**
 >
 > **Nothing running; $0; no perimeter contact.** `origin == local == a76ebe5`, all 5 tags on origin. **Remote is now SSH** (Carter registered `~/.ssh/id_rsa` on GitHub 2026-07-15) — pushes need **no PAT**; verify with `ssh -T git@github.com`.
 >
@@ -43,7 +59,7 @@ last_updated: 2026-06-11T15:30:00.000Z
 
 # RESUME HERE → cohort fully banked; durable-fix phase 2 ITEM 1 (read-side wiring) landed this session; GATE 1 cost + chr22 smoke are the open items
 
-> **2026-07-02T20:20Z (★★ LATEST ★★ — 🔥 LOOP FIRED + RUNNING on the AoU VM; region-1 gate in flight; fix + hardening pushed `2d23d67`; VM STAYS n1-standard-32, NO respec):**
+> **2026-07-02T20:20Z (SUPERSEDED — ⚠ THE LOOP IS NOT RUNNING: it was later STOPPED, banked 0/276, PID 5170 dead. This block's '🔥 LOOP FIRED + RUNNING' is HISTORY, not current state — do NOT act on it. Kept for the region-1 gate/diagnosis record; region-1 gate in flight; fix + hardening pushed `2d23d67`; VM STAYS n1-standard-32, NO respec):**
 > **The 2026-06-30 "transient" diagnosis below was WRONG** — corrected 2026-07-01. Region 1's real, reproducible failure was a **symmetry-check failure**: ~11 **monomorphic (MAC=0-in-AFR)** variants make plink emit `NaN` LD → `NaN!=NaN` breaks `read_square_bin`. Proven by running `read_square_bin` on the intact 42 GB `.ld.bin` (deterministic RAISE) + a pinpoint (12 NaN across 11 rows, diag 1.0). DECISION (Carter) = **DROP MAC=0**.
 > **FIX + HARDENING LANDED + PUSHED (`2d23d67`, origin==local; full `tests/m3` 321/30):** quick-260701-qcy adds `--mac 1 --nonfounders --write-snplist` to the SQUARE plink command (drops MAC=0 before `--r` → no NaN) + `_retained_window_bim` threads the plink `.snplist` so `n_var`/`.bim`/`.npz` align to the retained polymorphic set (`587c3d4`/`c56c715`). Hardening (`1a9d170`/`ed9cfd4`): H1 = a LOUD dup-SNP-id assertion (closes the one silent-misalignment path); H2 = `n_dropped_monomorphic` provenance (panel column + per-region stderr log). A 4-dimension **Fable-5 blast-radius** sweep + gsd-verifier (7/7) cleared it — downstream m3-04 `.rds`/SuSiE loaders align by **variant ID** so a retained subset is safe (and removes the NaN that would've broken Cholesky); banded/resume/egress/cost-model unaffected.
 > **NOW RUNNING:** Carter fired step 4 — the 276-region loop is RUNNING server-side on VM `AoU_Jupyter_ComputeEngine_20260626b` (n1-standard-32/120 GB), nohup + `timeout 312h`, run log `~/native_ld_loop.log`; region 1 computing. Steps 1–3 (pull `2d23d67` + re-gate + `.bim` col-2 uniqueness `awk`) passed pre-fire. **Do NOT restart the kernel.**
@@ -130,7 +146,7 @@ last_updated: 2026-06-11T15:30:00.000Z
 > **On the started cluster:** git pull+checkout -f; override Q-RS2 to **cores=1** for 64GB (`PYSPARK_SUBMIT_ARGS` cores=1/40g exec/12g overhead/24g driver — NOT yet in the notebook, paste inline); USE_DEV_SUBSET=True; run STEP 0 → **STEP A count-only** (`write_preflight_counts` → `m3-W2-preflight-counts.tsv`, all 15 dev cells incl. region_00143 real-MHC + region_00145__sub00) → option-B STOP/review → **STEP B** 3 cells (m2_region_00006 AFR, m2_region_00040__sub00 AFR + EUR; **watch EUR spill on 64GB** = the m3-04 viability signal) → **STEP C** stop+verify → push 3 artifacts → ping NCSU "probe-recorded" → Task 4.
 > STEP-A mechanism built+tested this session (commit 040002c; tests/m3 214 passed). Quota Tasks 1-2 closed. DO NOT run AOU-2 Cell 9 (compute) before STEP-B go; NEVER Cell 12 (egress). DO NOT start 20260620/20260617. Inspection VM stays up ($0.15/hr terminal). Full steps = `.planning/HANDOFF.json`. origin == local.
 
-> **2026-06-20 (★ LATEST ★ — m3-02c probe FULLY PREPPED + AoU STEP-0 inspection ALL-GREEN; PAUSED at the sized-cluster-start gate):** Pure NCSU code session — **nothing running, no cluster, $0.** Three quick tasks landed + PUSHED (origin == local **cb76115**): **260619-qjy** (A.3 AF sidecar gap CLOSED — `bm_to_npz.py` carries `allele_freq`), **260619-rqs** (post-split LD manifest regenerated via **Path B** — `--bed`/`--chain` gone so split the existing committed manifest reusing `_assemble_region_rows()`; `config/ld_regions.tsv` 322→434, 128 `__sub` @ `buffer_bp=10Mb`, dev manifest carries `m2_region_00040__sub00/01` AFR+EUR), **260619-vcp** (AOU-2 **gap-C3** WORKSPACE_BUCKET hard pin BAKED at cell idx 5 before the `_normalize_bucket` read + `cloned-mybucket` halt-assert). `tests/m3` 205/0/30. **The AoU Workbench agent ran a read-only STEP-0 inspection (cheap VM, no spend) → ALL preconditions GREEN on cb76115** and CAUGHT two real issues, both FIXED: origin was 32 commits behind (never pushed → pushed; memory `feedback_push_ncsu_before_aou_clone_fire`) + the gap-C3 bucket pin (→ vcp bake). **NEXT = run the m3-02c probe (autonomous:false, COSTS MONEY):** `/gsd-execute-phase m3` records the pre-satisfied quota (N2=5000) → pauses at Task 3 for the AoU fire → Carter authorizes the sized-cluster start → bucket-pin cell → Q-RS2 → STEP A preflight → **PAUSE** → STEP B (≥3 cells: 00006 AFR + 00040__sub00 AFR + 00040__sub00 EUR mandatory + HLA 00145) under cost controls → data-layer-verify → STEP C shutdown → 3 artifacts → Task 4 cost model + go/no-go. **PENDING (re-offer before boot):** how to authorize the ~$25-30/hr start — (A) start+stay, (B) start+stop-between-A-and-B, (C) hold (Carter's spend call). Primary resume = `.planning/HANDOFF.json`. SUPERSEDES the 2026-06-19 block below.
+> **2026-06-20 (SUPERSEDED — m3-02c probe FULLY PREPPED + AoU STEP-0 inspection ALL-GREEN; PAUSED at the sized-cluster-start gate):** Pure NCSU code session — **nothing running, no cluster, $0.** Three quick tasks landed + PUSHED (origin == local **cb76115**): **260619-qjy** (A.3 AF sidecar gap CLOSED — `bm_to_npz.py` carries `allele_freq`), **260619-rqs** (post-split LD manifest regenerated via **Path B** — `--bed`/`--chain` gone so split the existing committed manifest reusing `_assemble_region_rows()`; `config/ld_regions.tsv` 322→434, 128 `__sub` @ `buffer_bp=10Mb`, dev manifest carries `m2_region_00040__sub00/01` AFR+EUR), **260619-vcp** (AOU-2 **gap-C3** WORKSPACE_BUCKET hard pin BAKED at cell idx 5 before the `_normalize_bucket` read + `cloned-mybucket` halt-assert). `tests/m3` 205/0/30. **The AoU Workbench agent ran a read-only STEP-0 inspection (cheap VM, no spend) → ALL preconditions GREEN on cb76115** and CAUGHT two real issues, both FIXED: origin was 32 commits behind (never pushed → pushed; memory `feedback_push_ncsu_before_aou_clone_fire`) + the gap-C3 bucket pin (→ vcp bake). **NEXT = run the m3-02c probe (autonomous:false, COSTS MONEY):** `/gsd-execute-phase m3` records the pre-satisfied quota (N2=5000) → pauses at Task 3 for the AoU fire → Carter authorizes the sized-cluster start → bucket-pin cell → Q-RS2 → STEP A preflight → **PAUSE** → STEP B (≥3 cells: 00006 AFR + 00040__sub00 AFR + 00040__sub00 EUR mandatory + HLA 00145) under cost controls → data-layer-verify → STEP C shutdown → 3 artifacts → Task 4 cost model + go/no-go. **PENDING (re-offer before boot):** how to authorize the ~$25-30/hr start — (A) start+stay, (B) start+stop-between-A-and-B, (C) hold (Carter's spend call). Primary resume = `.planning/HANDOFF.json`. SUPERSEDES the 2026-06-19 block below.
 >
 > **2026-06-19 (SUPERSEDED by the 2026-06-20 block above — m3-02b EXECUTED + adversarially reviewed + CR-01/warnings fixed + blast-radius swept; NEXT = m3-02c):** Pure NCSU code session — **nothing running, no cluster, no cost.** **Executed `m3-02b`** (Wave 0): overlapping-window xlarge split (`build_ld_region_manifest.py`, half-open cores + core±buffer windows + explicit `buffer_bp`) + dev tuple-resolve/capped-expansion + AF metadata in `aou_ld_panel.py` `.npz`; **NEW** `stitch_subregions_to_rds.R` **BANDED** sparse stitch (cross-core pairs within `buffer_bp` retained, beyond zeroed; `obj$R`+`obj$variants` for the real `load_ld_matrix`); A6 real-loader verify + sparse-parent benchmark + AOU-2 Q-RS2 cell; provisioned the `m3-r-ld` conda env for the no-skip R families (`a17a47a`/`0e3ec43`/`908de71`/`989f53b`). **Adversarial deep review** confirmed the banded-stitch geometry correct (fuzz-verified) + found **CR-01** (critical) + WR-01/02/03 (`fef84eb`). **Fixed CR-01 + all warnings** TDD RED-first (`f96fbb9`): CR-01 = honor the `.npz` `lower_triangular` flag (old `!isSymmetric` gate DOUBLED full-matrix off-diagonals r→2r). **Blast-radius sweep** (4 parallel agents, `b34dc60`) caught **BR-01** — the CR-01 fix made the flag authoritative but `bm_to_npz.py` (Path A.3, the xlarge-split deliverable path) never wrote it → A.3 off-diagonals **HALVED** (0.6→0.30); **fixed** with 2 RED-first tests (`1a06471`); a stale liftover test was also exposed + corrected (UCSC `hg38ToHg19` chain truth **53843159**, not dbSNP 53803574). **Full `pytest tests/m3` = 194 passed / 0 failed / 30 skipped.** **DEFERRED + tracked (m3-04 precondition):** `bm_to_npz.py` writes no `allele_freq` → Path A.3 regions get NA AF (todo `530ae5d` + m3-02c carry-forward note `0d265c9` + `m3-02b-W2-rescope-BLAST-RADIUS-FIX.md`). **NEXT = `m3-02c`** (quota + real-cohort cost probe + go/no-go; `autonomous:false`; Carter fires in-perimeter, costs money); open flag: `--subregion-buffer-mb 10` effectively mandatory (radius default spans the whole parent). Primary resume = `.planning/HANDOFF.json`. SUPERSEDES the 2026-06-18 dev-10-killed block below (still valid history: dev-10 on 64-vCPU/16 GB is intractable; the SPLIT done in m3-02b is the structural fix).
 >
```
rc=0

#### The live `HANDOFF.json:14` retraction (the CLAIM UNDER TEST, quoted as a claim)

`$ sed -n '14p' .planning/HANDOFF.json | cut -c1-900`

```
    "K-3 CLOSED: run_susie_rss.R:1018-1019 reads 1,909/1,900; grep for the stale 1,944/1,935 returns 0.",
```
rc=0

`$ grep -n 'SR4-OPEN' .planning/HANDOFF.json | cut -c1-300`

```
9:  "status": "All blast-radius gate rows CLEAR; the freeze mechanism correctly scoped; E-2 disposed as A. NO Carter DECISION is outstanding. What remains: three E-2 disclosure obligations, the SR4-OPEN question, K-2 (extraction declined on fire-path risk), K-3 (CLOSED), and m3-04c Task 3 — the term
118:    "▶ SR4-OPEN (a QUESTION, not a blocker) — FIVE files the project has been calling \"frozen\" were never enforced by anything AND have drifted: occlusion_manifest.py (+46/-8), occlusion_present_rate_scan.py (+154/-21), drop_occluded_from_sumstats.py (+97/-24), ld_npz_to_rds.R (+313/-62), pipe
```
rc=0

`$ grep -rn 'SR4-OPEN' .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md | cut -c1-300`

```
989:## ⚠ SR4-OPEN — FIVE files `HANDOFF.json` calls "frozen at `bf16289`" have MOVED. A QUESTION FOR CARTER, deliberately NOT answered.
```
rc=0

### D3 — STEP 5c: anywhere else? (scoped search; `results/` NEVER touched)

⚠ Scope is `.planning/ src/ tests/ config/` only. `results/` and
`results/legacy/` are symlinks into `/rs1` and `grep -r` does not follow
symlinks on this tree; they are irrelevant to these five paths and were
deliberately never searched.

#### `occlusion_manifest.py`

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'occlusion_manifest.py' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | wc -l`

```
22
```
rc=0

`$ grep -rln --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'occlusion_manifest.py' .planning/ src/ tests/ config/ | xargs -r grep -lE 'frozen|freeze|pinned' 2>/dev/null | head -20`

```
.planning/STATE.md
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-PLAN.md
.planning/quick/260715-sqe-resolve-m3-07b-panel-column-test-vs-test/260715-sqe-UAT.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-VERIFICATION.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-PLAN.md
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-PLAN.md
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-PLAN.md
.planning/quick/260715-u22-close-blast-radius-findings-scan-enrich-/260715-u22-VERIFICATION.md
.planning/quick/260715-u22-close-blast-radius-findings-scan-enrich-/260715-u22-PLAN.md
.planning/quick/260715-u22-close-blast-radius-findings-scan-enrich-/260715-u22-SUMMARY.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07c-W7-present-rate-and-lockstep-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07a-W7-osf-gate-and-red-scaffold-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07a-UAT.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07b-W7-span-filter-and-manifest-SUMMARY.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07-RESEARCH.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md
.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
```
rc=0

Up to 5 representative lines (truncated from the count above):

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'occlusion_manifest.py' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | cut -c1-260 | head -5`

```
.planning/STATE.md:17:last_activity: "2026-08-04 (LATEST — SESSION CLOSE) — ⛔ m3-04c HALTED after the m3-04b BLAST-RADIUS sweep (4 independent read-only investigators + orchestrator verification; $0, NC State, no perimeter, ZERO source drift). Resumed via /gsd
.planning/STATE.md:39:**⚠⚠ A CLAIM IN OUR OWN HANDOFF WAS FALSE AND IS RETRACTED.** *"All 7 pinned files 0-line diff vs `bf16289`"* — `bf16289` appears in **ZERO** places across `src/`, `tests/`, `config/`, `Snakefile`: **nothing ever enforced it**, and **5 of
.planning/STATE.md:311:> **⛔ NEXT = PAUSE. 07b/07c are UNBLOCKED but NOT AUTHORIZED** — Carter's standing instruction is "07a then PAUSE". 07b = production code (`occlusion_span_filter.py`, `--exclude` wiring in `run_native_ld_panel.py` + `aou_ld_panel.py`, `_
.planning/STATE.md:1607:| 260715-u22 | **Closed BOTH blast-radius findings from the 2026-07-15 4-agent sweep — two PRE-EXISTING defects, TDD RED-first, one atomic commit each (different gates → independently revertible).** Neither was caused by quick-260715-sq
.planning/STATE.md:1614:| 260804-rtc | **Landed the four autonomous `$0` correctness fixes the m3-04b blast radius cleared — every one of them a SILENT-failure class, and all four cheap now / expensive after an 11-day fire.** Ordered by Carter at a `/gsd-resum
```
rc=0

#### `occlusion_present_rate_scan.py`

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'occlusion_present_rate_scan.py' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | wc -l`

```
19
```
rc=0

`$ grep -rln --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'occlusion_present_rate_scan.py' .planning/ src/ tests/ config/ | xargs -r grep -lE 'frozen|freeze|pinned' 2>/dev/null | head -20`

```
.planning/STATE.md
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-PLAN.md
.planning/quick/260715-sqe-resolve-m3-07b-panel-column-test-vs-test/260715-sqe-SUMMARY.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-VERIFICATION.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-PLAN.md
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-PLAN.md
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-PLAN.md
.planning/quick/260715-u22-close-blast-radius-findings-scan-enrich-/260715-u22-VERIFICATION.md
.planning/quick/260715-u22-close-blast-radius-findings-scan-enrich-/260715-u22-PLAN.md
.planning/quick/260715-u22-close-blast-radius-findings-scan-enrich-/260715-u22-SUMMARY.md
.planning/quick/260715-vxz-fix-p3-gsutil-blip-bucket-overwrite-dest/260715-vxz-VERIFICATION.md
.planning/quick/260715-vxz-fix-p3-gsutil-blip-bucket-overwrite-dest/260715-vxz-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07c-W7-present-rate-and-lockstep-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07a-W7-osf-gate-and-red-scaffold-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07c-W7-present-rate-and-lockstep-SUMMARY.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07-RESEARCH.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md
```
rc=0

Up to 5 representative lines (truncated from the count above):

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'occlusion_present_rate_scan.py' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | cut -c1-260 | head -5`

```
.planning/STATE.md:39:**⚠⚠ A CLAIM IN OUR OWN HANDOFF WAS FALSE AND IS RETRACTED.** *"All 7 pinned files 0-line diff vs `bf16289`"* — `bf16289` appears in **ZERO** places across `src/`, `tests/`, `config/`, `Snakefile`: **nothing ever enforced it**, and **5 of
.planning/STATE.md:266:> **⚠ D-04b-01 — A REAL DEFECT FOUND, DELIBERATELY NOT FIXED** (both modules are 0-diff-pinned): `bmi.AFR.PAGE.2019.GRCh37.tsv.bgz` stores POS as the **float string `5982778.0`**, and `int("5982778.0")` **raises** in `_canonical_key` in 
.planning/STATE.md:278:> **★ m3-07c LANDED** — authorized by Carter's **"Proceed"** in direct response to *"your explicit go is the only thing gating it."* NEW: `src/python/occlusion_present_rate_scan.py` (`scan_present_rate`; 6 RED → **6 passed**) + `src/pyth
.planning/STATE.md:301:> **⛔ NEXT = PAUSE. 07c NOT started** (Carter: "07b then PAUSE"). 07c = `occlusion_present_rate_scan.py` + `drop_occluded_from_sumstats.py`, and it populates the `traits_present`/`n_traits_present`/`n_traits_scanned` seam already DECLARE
.planning/STATE.md:311:> **⛔ NEXT = PAUSE. 07b/07c are UNBLOCKED but NOT AUTHORIZED** — Carter's standing instruction is "07a then PAUSE". 07b = production code (`occlusion_span_filter.py`, `--exclude` wiring in `run_native_ld_panel.py` + `aou_ld_panel.py`, `_
```
rc=0

#### `drop_occluded_from_sumstats.py`

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'drop_occluded_from_sumstats.py' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | wc -l`

```
18
```
rc=0

`$ grep -rln --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'drop_occluded_from_sumstats.py' .planning/ src/ tests/ config/ | xargs -r grep -lE 'frozen|freeze|pinned' 2>/dev/null | head -20`

```
.planning/STATE.md
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-PLAN.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-VERIFICATION.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-PLAN.md
.planning/quick/260806-b77-close-the-remaining-blast-radius-finding/260806-b77-VERIFICATION.md
.planning/quick/260806-b77-close-the-remaining-blast-radius-finding/260806-b77-SUMMARY.md
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-PLAN.md
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-PLAN.md
.planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t/260805-w7u-SUMMARY.md
.planning/quick/260715-u22-close-blast-radius-findings-scan-enrich-/260715-u22-VERIFICATION.md
.planning/quick/260715-u22-close-blast-radius-findings-scan-enrich-/260715-u22-PLAN.md
.planning/quick/260715-u22-close-blast-radius-findings-scan-enrich-/260715-u22-SUMMARY.md
.planning/quick/260715-vxz-fix-p3-gsutil-blip-bucket-overwrite-dest/260715-vxz-VERIFICATION.md
.planning/quick/260715-vxz-fix-p3-gsutil-blip-bucket-overwrite-dest/260715-vxz-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07c-W7-present-rate-and-lockstep-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-07c-W7-present-rate-and-lockstep-SUMMARY.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md
```
rc=0

Up to 5 representative lines (truncated from the count above):

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'drop_occluded_from_sumstats.py' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | cut -c1-260 | head -5`

```
.planning/STATE.md:39:**⚠⚠ A CLAIM IN OUR OWN HANDOFF WAS FALSE AND IS RETRACTED.** *"All 7 pinned files 0-line diff vs `bf16289`"* — `bf16289` appears in **ZERO** places across `src/`, `tests/`, `config/`, `Snakefile`: **nothing ever enforced it**, and **5 of
.planning/STATE.md:266:> **⚠ D-04b-01 — A REAL DEFECT FOUND, DELIBERATELY NOT FIXED** (both modules are 0-diff-pinned): `bmi.AFR.PAGE.2019.GRCh37.tsv.bgz` stores POS as the **float string `5982778.0`**, and `int("5982778.0")` **raises** in `_canonical_key` in 
.planning/STATE.md:278:> **★ m3-07c LANDED** — authorized by Carter's **"Proceed"** in direct response to *"your explicit go is the only thing gating it."* NEW: `src/python/occlusion_present_rate_scan.py` (`scan_present_rate`; 6 RED → **6 passed**) + `src/pyth
.planning/STATE.md:301:> **⛔ NEXT = PAUSE. 07c NOT started** (Carter: "07b then PAUSE"). 07c = `occlusion_present_rate_scan.py` + `drop_occluded_from_sumstats.py`, and it populates the `traits_present`/`n_traits_present`/`n_traits_scanned` seam already DECLARE
.planning/STATE.md:311:> **⛔ NEXT = PAUSE. 07b/07c are UNBLOCKED but NOT AUTHORIZED** — Carter's standing instruction is "07a then PAUSE". 07b = production code (`occlusion_span_filter.py`, `--exclude` wiring in `run_native_ld_panel.py` + `aou_ld_panel.py`, `_
```
rc=0

#### `ld_npz_to_rds.R`

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'ld_npz_to_rds.R' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | wc -l`

```
68
```
rc=0

`$ grep -rln --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'ld_npz_to_rds.R' .planning/ src/ tests/ config/ | xargs -r grep -lE 'frozen|freeze|pinned' 2>/dev/null | head -20`

```
.planning/ROADMAP.md
.planning/amendments/AOU-LD-PIPELINE.md
.planning/STATE.md
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-PLAN.md
.planning/quick/260715-sqe-resolve-m3-07b-panel-column-test-vs-test/260715-sqe-UAT.md
.planning/quick/260715-sqe-resolve-m3-07b-panel-column-test-vs-test/260715-sqe-PLAN.md
.planning/quick/260715-sqe-resolve-m3-07b-panel-column-test-vs-test/260715-sqe-SUMMARY.md
.planning/quick/260806-pd3-close-blast-radius-finding-k-1-restore-v/260806-pd3-PLAN.md
.planning/quick/260806-pd3-close-blast-radius-finding-k-1-restore-v/260806-pd3-SUMMARY.md
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-SUMMARY.md
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-PLAN.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-VERIFICATION.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-PLAN.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-SUMMARY.md
.planning/quick/260806-b77-close-the-remaining-blast-radius-finding/260806-b77-PLAN.md
.planning/quick/260806-b77-close-the-remaining-blast-radius-finding/260806-b77-VERIFICATION.md
.planning/quick/260806-b77-close-the-remaining-blast-radius-finding/260806-b77-SUMMARY.md
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-PLAN.md
.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md
.planning/quick/260803-jag-rectify-uncommitted-working-tree-state-r/260803-jag-PLAN.md
```
rc=0

Up to 5 representative lines (truncated from the count above):

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'ld_npz_to_rds.R' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | cut -c1-260 | head -5`

```
.planning/ROADMAP.md:213:- [ ] m3-06-W6-ld-nan-psd-conditioning-PLAN.md — Wave 6 (999.1 §2-4 promotion; autonomous NCSU code, planned 2026-07-07): the AFR native-panel NaN conditioning MACHINERY under the posted OSF amendment (`tcujq`). **T1** — refactor the t
.planning/ROADMAP.md:1077:   panel `.npz` contract frozen (`ld_npz_to_rds.R` unchanged).
.planning/STATE.md:15:# Frozen contracts byte-unchanged (plink_ld_to_npz.py / ld_npz_to_rds.R / condition_ld_matrix.py all git-diff EMPTY).
.planning/STATE.md:17:last_activity: "2026-08-04 (LATEST — SESSION CLOSE) — ⛔ m3-04c HALTED after the m3-04b BLAST-RADIUS sweep (4 independent read-only investigators + orchestrator verification; $0, NC State, no perimeter, ZERO source drift). Resumed via /gsd
.planning/STATE.md:39:**⚠⚠ A CLAIM IN OUR OWN HANDOFF WAS FALSE AND IS RETRACTED.** *"All 7 pinned files 0-line diff vs `bf16289`"* — `bf16289` appears in **ZERO** places across `src/`, `tests/`, `config/`, `Snakefile`: **nothing ever enforced it**, and **5 of
```
rc=0

#### `pipeline.schema.yaml`

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'pipeline.schema.yaml' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | wc -l`

```
18
```
rc=0

`$ grep -rln --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'pipeline.schema.yaml' .planning/ src/ tests/ config/ | xargs -r grep -lE 'frozen|freeze|pinned' 2>/dev/null | head -20`

```
.planning/STATE.md
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-PLAN.md
.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran/260805-23d-SUMMARY.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-VERIFICATION.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-PLAN.md
.planning/quick/260805-o7o-close-blast-radius-findings-h-and-i-alle/260805-o7o-SUMMARY.md
.planning/quick/260806-b77-close-the-remaining-blast-radius-finding/260806-b77-PLAN.md
.planning/quick/260806-b77-close-the-remaining-blast-radius-finding/260806-b77-VERIFICATION.md
.planning/quick/260806-b77-close-the-remaining-blast-radius-finding/260806-b77-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-PLAN.md
.planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t/260805-w7u-SUMMARY.md
.planning/quick/260805-w7u-close-blast-radius-finding-e-crosswalk-t/260805-w7u-PLAN.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md
.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md
.planning/phases/05-pathway-partitioned-heritability/05-REVIEW.md
.planning/phases/05-pathway-partitioned-heritability/05-01-PLAN.md
.planning/phases/00-data-access-infrastructure/00-RESEARCH.md
```
rc=0

Up to 5 representative lines (truncated from the count above):

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'pipeline.schema.yaml' .planning/ src/ tests/ config/ | grep -iE 'frozen|freeze|pinned' | cut -c1-260 | head -5`

```
.planning/STATE.md:39:**⚠⚠ A CLAIM IN OUR OWN HANDOFF WAS FALSE AND IS RETRACTED.** *"All 7 pinned files 0-line diff vs `bf16289`"* — `bf16289` appears in **ZERO** places across `src/`, `tests/`, `config/`, `Snakefile`: **nothing ever enforced it**, and **5 of
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-PLAN.md:371:    <automated>D=.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-; test -s $D/260811-pmv-EVIDENCE.md && test -s $D/260811-pmv-evidence.tsv && [ "$(awk
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-PLAN.md:499:    <automated>D=.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-; test -s $D/260811-pmv-DOSSIER.md && [ "$(wc -l < $D/260811-pmv-DOSSIER.md)" -ge 150
.planning/quick/260806-b77-close-the-remaining-blast-radius-finding/260806-b77-PLAN.md:382:    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git diff --exit-code dc4bbd2 -- src/legacy/region_analysis/scripts/run_susie_rss.R && echo F
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-SUMMARY.md:83:| `src/snakemake/schemas/pipeline.schema.yaml` | **+119 / −0** | 2026-08-06 (`2563451`) | ⚠ **MOVED — NOT gated** |
```
rc=0

#### Where the pin SHA `bf16289` appears at all, repo-scoped

`$ grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'bf16289' .planning/ src/ tests/ config/ | wc -l`

```
104
```
rc=0

`$ grep -rln --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' --include='*.yml' --include='*.smk' --include='*.json' 'bf16289' .planning/ src/ tests/ config/`

```
.planning/DECISIONS.md
.planning/STATE.md
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-PLAN.md
.planning/quick/260803-jag-rectify-uncommitted-working-tree-state-r/260803-jag-PLAN.md
.planning/quick/260803-jag-rectify-uncommitted-working-tree-state-r/260803-jag-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-SUMMARY.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-PLAN.md
.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-VERIFICATION.md
.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md
.planning/HANDOFF.json
tests/m3/test_source_freeze_pins.py
```
rc=0

And in the FIRE PATH / source dirs only (the sr4 finding: enforced by nothing):

`$ grep -rn 'bf16289' src/ config/ | wc -l`

```
0
```
rc=0

`$ grep -rn 'bf16289' tests/ | wc -l`

```
grep: tests/m3/__pycache__/test_source_freeze_pins.cpython-311-pytest-9.0.3.pyc: binary file matches
grep: tests/m3/__pycache__/test_source_freeze_pins.cpython-311.pyc: binary file matches
5
```
rc=0

`$ grep -rn 'bf16289' tests/ | cut -c1-200`

```
grep: tests/m3/__pycache__/test_source_freeze_pins.cpython-311-pytest-9.0.3.pyc: binary file matches
grep: tests/m3/__pycache__/test_source_freeze_pins.cpython-311.pyc: binary file matches
tests/m3/test_source_freeze_pins.py:48:#: 2026-07-16 freeze declaration (``bf16289``). A CODE pin: comment and
tests/m3/test_source_freeze_pins.py:52:PY_CODE_REF = "bf16289"
tests/m3/test_source_freeze_pins.py:90:#: bf16289". FOUR of these five are named there and every one of them has MOVED;
tests/m3/test_source_freeze_pins.py:91:#: ``git diff --numstat bf16289 HEAD`` measured 2026-08-06:
tests/m3/test_source_freeze_pins.py:179:    """``HANDOFF.json:14``'s "All 7 pinned files 0-line diff vs bf16289" is FALSE
```
rc=0
## STEP 5d — was `bf16289` enforced by ANY test AT THE TIME OF THE DRIFT?

STEP 7's `NEVER-FROZEN` branch requires this, and it is a claim about
2026-08-03..2026-08-06 -- NOT about today. Measured at each drift commit
itself, not inferred from the register.

`$ git grep -c 'bf16289' d7dfa67 -- tests/ src/ config/ Snakefile 2>&1 | wc -l`

```
0
```
rc=0

`$ git grep -c 'bf16289' 3bb8783 -- tests/ src/ config/ Snakefile 2>&1 | wc -l`

```
0
```
rc=0

`$ git grep -c 'bf16289' bf963df -- tests/ src/ config/ Snakefile 2>&1 | wc -l`

```
0
```
rc=0

`$ git grep -c 'bf16289' fac9a93 -- tests/ src/ config/ Snakefile 2>&1 | wc -l`

```
0
```
rc=0

`$ git grep -c 'bf16289' aeed8c0 -- tests/ src/ config/ Snakefile 2>&1 | wc -l`

```
0
```
rc=0

`$ git grep -c 'bf16289' 57b381f -- tests/ src/ config/ Snakefile 2>&1 | wc -l`

```
0
```
rc=0

`$ git grep -c 'bf16289' 64f420a -- tests/ src/ config/ Snakefile 2>&1 | wc -l`

```
0
```
rc=0

`$ git grep -c 'bf16289' 2563451 -- tests/ src/ config/ Snakefile 2>&1 | wc -l`

```
0
```
rc=0

And today, for contrast:

`$ git grep -c 'bf16289' HEAD -- tests/ src/ config/`

```
HEAD:tests/m3/test_source_freeze_pins.py:5
```
rc=0

`$ git grep -n 'bf16289' HEAD -- src/ config/ | wc -l`

```
0
```
rc=0

## STEP 6 — gated TODAY?

### The pin constants, verbatim from `tests/m3/test_source_freeze_pins.py`

`$ grep -n 'PY_CODE_REF = ' tests/m3/test_source_freeze_pins.py`

```
52:PY_CODE_REF = "bf16289"
103:MOVED_SINCE_PY_CODE_REF = (
```
rc=0

`$ sed -n '/^#: The three files AUTH-SR4-EXTEND covers/,/^)/p' tests/m3/test_source_freeze_pins.py`

```
#: The three files AUTH-SR4-EXTEND covers -- MEASURED 0-diff against
#: ``PY_CODE_REF`` before they were gated. Adding a file here requires a
#: RECORDED DECISION that it is frozen, not an inference.
PY_FROZEN_RELS = (
    "src/python/plink_ld_to_npz.py",
    "src/python/condition_ld_matrix.py",
    "src/python/occlusion_span_filter.py",
)
```
rc=0

`$ sed -n '/^#: ⚠ ..\.planning\/HANDOFF.json:14/,/^)/p' tests/m3/test_source_freeze_pins.py`

```
#: ⚠ ``.planning/HANDOFF.json:14`` claims "All 7 pinned files 0-line diff vs
#: bf16289". FOUR of these five are named there and every one of them has MOVED;
#: ``git diff --numstat bf16289 HEAD`` measured 2026-08-06:
#:
#:   occlusion_manifest.py            +46  / -8    (bf963df, 2026-08-04)
#:   occlusion_present_rate_scan.py   +154 / -21   (fac9a93, 2026-08-04)
#:   drop_occluded_from_sumstats.py   +97  / -24   (bf963df, 2026-08-04)
#:   ld_npz_to_rds.R                  +313 / -62   (57b381f, 2026-08-05)
#:   pipeline.schema.yaml             +119 / -0    (2563451, 2026-08-06)
#:
#: Declaring a moving file frozen is a DECISION, not an inference, and gating a
#: file that changed three times in three days would manufacture exactly the
#: nuisance-repin timebomb this rescope exists to remove. They are registered as
#: an OPEN QUESTION for Carter in deferred-items.md and deliberately NOT gated.
MOVED_SINCE_PY_CODE_REF = (
    "src/python/occlusion_manifest.py",
    "src/python/occlusion_present_rate_scan.py",
    "src/python/drop_occluded_from_sumstats.py",
    "src/scripts/ld_npz_to_rds.R",
    "src/snakemake/schemas/pipeline.schema.yaml",
)
```
rc=0

### `test_the_handoff_frozen_claim_is_recorded_as_partly_false`, verbatim

⚠ THE COST OF GATING ANY OF THE FIVE IS IN THIS BODY: the second assertion
requires each of the five to still have a NON-EMPTY numstat, and the first
requires each to be OUT of `PY_FROZEN_RELS`. Adding any of the five to the
gate makes this test go RED.

`$ sed -n '/^def test_the_handoff_frozen_claim_is_recorded_as_partly_false/,/^# ===/p' tests/m3/test_source_freeze_pins.py`

```
def test_the_handoff_frozen_claim_is_recorded_as_partly_false():
    """``HANDOFF.json:14``'s "All 7 pinned files 0-line diff vs bf16289" is FALSE
    for 5 of 8. Recorded here so a future sweep cannot "helpfully" add them back
    without a decision, and so the record itself stays honest."""
    for rel in MOVED_SINCE_PY_CODE_REF:
        assert rel not in PY_FROZEN_RELS, (
            f"{rel} has MOVED since {PY_CODE_REF} and must not be gated against "
            "it -- declaring a moving file frozen is a DECISION for Carter, not "
            "an inference (see deferred-items.md)"
        )
        numstat = _git("diff", "--numstat", PY_CODE_REF, "HEAD", "--", rel).stdout.strip()
        assert numstat, (
            f"{rel} is now 0-diff vs {PY_CODE_REF}. The recorded finding "
            "(HANDOFF's claim is false for 5 of 8 files) has changed -- re-open "
            "the question rather than editing this list"
        )
    for rel in PY_FROZEN_RELS:
        numstat = _git("diff", "--numstat", PY_CODE_REF, "HEAD", "--", rel).stdout.strip()
        assert not numstat, (
            f"{rel} is NO LONGER 0-diff vs {PY_CODE_REF} ({numstat!r}); it left "
            "the measured basis for AUTH-SR4-EXTEND"
        )


# ==========================================================================
```
rc=0

### Which languages does the freeze utility support? (this bounds the cost of gating F4/F5)

`$ grep -n '^LANG_R\|^LANG_PY\|unsupported lang' tests/m3/source_freeze.py`

```
108:LANG_R = "r"
109:LANG_PY = "py"
373:    raise AssertionError(f"unsupported lang {lang!r}; expected {LANG_R!r} or {LANG_PY!r}")
383:    raise AssertionError(f"unsupported lang {lang!r}; expected {LANG_R!r} or {LANG_PY!r}")
397:    raise AssertionError(f"unsupported lang {lang!r}; expected {LANG_R!r} or {LANG_PY!r}")
```
rc=0

`$ grep -c -i 'yaml' tests/m3/source_freeze.py`

```
0
```
rc=1

### THE LIVE GATE

`$ /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_source_freeze_pins.py -q 2>&1 | tail -8`

```
.......................................                                  [100%]
39 passed in 1.26s
```
rc=0

## The SR4-OPEN question, VERBATIM as posed (the CLAIM/QUESTION under test)

From `.planning/HANDOFF.json`:

`$ grep -n 'SR4-OPEN' .planning/HANDOFF.json | sed -n '2p' | cut -c1-1800`

```
118:    "▶ SR4-OPEN (a QUESTION, not a blocker) — FIVE files the project has been calling \"frozen\" were never enforced by anything AND have drifted: occlusion_manifest.py (+46/-8), occlusion_present_rate_scan.py (+154/-21), drop_occluded_from_sumstats.py (+97/-24), ld_npz_to_rds.R (+313/-62), pipeline.schema.yaml (+119/-0). Were they frozen-and-drifted (in which case the drift needs review) or never actually frozen (in which case the handoff language was wrong)? Nothing is blocked on the answer; the 3 genuinely-0-diff files are now gated for real."
```
rc=0

From the phase `deferred-items.md`:

`$ grep -n 'never actually frozen' .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md | cut -c1-900`

```
```
rc=0

`$ grep -n 'SR4\|frozen and have since drifted' .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md | cut -c1-400 | head -20`

```
459:⚠ **SUPERSEDED 2026-08-06 by `quick-260806-sr4`** (`AUTH-SR4-RESCOPE`): the forward gate is now `pytest tests/m3/test_source_freeze_pins.py` — a **CODE** pin, not a byte pin — and the constants are `FROZEN_R_CODE_REV` / `FREEZE_CODE_REF`, both **import aliases** of the single `R_CODE_REF` in `tests/m3/test_source_freeze_pins.py`. The historical sentences around this note are left exactly as wr
605:⚠ **SUPERSEDED 2026-08-06 by `quick-260806-sr4`** (`AUTH-SR4-RESCOPE`): the forward gate is now `pytest tests/m3/test_source_freeze_pins.py` — a **CODE** pin, not a byte pin — and the constants are `FROZEN_R_CODE_REV` / `FREEZE_CODE_REF`, both **import aliases** of the single `R_CODE_REF` in `tests/m3/test_source_freeze_pins.py`. The historical sentences around this note are left exactly as wr
718:⚠ **SUPERSEDED 2026-08-06 by `quick-260806-sr4`** (`AUTH-SR4-RESCOPE`): the forward gate is now `pytest tests/m3/test_source_freeze_pins.py` — a **CODE** pin, not a byte pin — and the constants are `FROZEN_R_CODE_REV` / `FREEZE_CODE_REF`, both **import aliases** of the single `R_CODE_REF` in `tests/m3/test_source_freeze_pins.py`. The historical sentences around this note are left exactly as wr
723:**Status: ✅ CLOSED. `AUTH-SR4-K3` GRANTED (Carter, 2026-08-06) and SPENT.**
736:**CODE** under `AUTH-SR4-RESCOPE`, so **the freeze no longer covers comments at
989:## ⚠ SR4-OPEN — FIVE files `HANDOFF.json` calls "frozen at `bf16289`" have MOVED. A QUESTION FOR CARTER, deliberately NOT answered.
1015:**Why three were gated and five were not.** `AUTH-SR4-EXTEND` covers only files
1026:**frozen and have since drifted** (in which case something was changed that
```
rc=0

The retraction that already landed (`HANDOFF.json`):

`$ grep -n 'RETRACTED\|retracted' .planning/HANDOFF.json | cut -c1-1200`

```
18:    "⚠⚠ RETRACTION — the earlier claim 'All 7 pinned files 0-line diff vs bf16289' is FALSE. bf16289 appears in ZERO places across src/, tests/, config/, Snakefile (nothing ever enforced it) and 5 of the 8 files had MOVED: occlusion_manifest.py +46/-8, occlusion_present_rate_scan.py +154/-21, drop_occluded_from_sumstats.py +97/-24, ld_npz_to_rds.R +313/-62, pipeline.schema.yaml +119/-0. Only plink_ld_to_npz.py, condition_ld_matrix.py and occlusion_span_filter.py are genuinely 0-diff — those three are NOW GATED FOR REAL. Do not repeat the retracted claim.",
35:    "quick-260806-sr4 (98e0ee9, 656529a, c04e672, 5f0520b)": "RESCOPED the source freeze from BYTES to CODE and CLOSED K-3. Triggered by Carter's question \"why is anything frozen?\". Built tests/m3/source_freeze.py — a comment-insensitive, string-literal-aware code pin. THREE DISCOVERIES worth more than the change itself: (1) bf16289, the SHA the handoff claimed pinned 7 files, has ZERO enforcement anywhere and 5 of those 8 files had MOVED — retracted above; (2) the repo already held NINE ad-hoc comment-strippers, two in the very file being edited, so this is a consolidation, not an invention; (3) the plan-checker's multi-line fixture exposed a REAL BUG in the masker — masking the newline inside a string dropped every subsequent line, and `len(masked) == len(text)` is STRUCTURALLY BLIND to it, so the length invariant alone would never have caught it. The plan took THREE adversarial rounds (two full check cycles plus an orchestrator constrained-fix pass landing 13 more fixes); the checker's own fixes twice introduced new defects, which is why the last pass forbade adding anything."
```
rc=0

## The RESIDUAL LIVE claim sites (for the Carter's-decision block)

These are CURRENT-STATE assertions in live narrative files, as distinct from
historical records inside past PLAN/SUMMARY/VERIFICATION artifacts (which are
legitimately historical and are NOT correction sites). Scope:
`STATE.md`, `HANDOFF.json`, `ROADMAP.md`, `.continue-here.md`, `deferred-items.md`.

#### `.planning/STATE.md`

`$ grep -nE 'occlusion_manifest\.py|occlusion_present_rate_scan\.py|drop_occluded_from_sumstats\.py|ld_npz_to_rds\.R|pipeline\.schema\.yaml' .planning/STATE.md | grep -iE 'frozen|freeze|pinned' | cut -c1-300`

```
15:# Frozen contracts byte-unchanged (plink_ld_to_npz.py / ld_npz_to_rds.R / condition_ld_matrix.py all git-diff EMPTY).
17:last_activity: "2026-08-04 (LATEST — SESSION CLOSE) — ⛔ m3-04c HALTED after the m3-04b BLAST-RADIUS sweep (4 independent read-only investigators + orchestrator verification; $0, NC State, no perimeter, ZERO source drift). Resumed via /gsd-resume-work --auto --chain and DELIBERATELY DID NOT EXECUT
39:**⚠⚠ A CLAIM IN OUR OWN HANDOFF WAS FALSE AND IS RETRACTED.** *"All 7 pinned files 0-line diff vs `bf16289`"* — `bf16289` appears in **ZERO** places across `src/`, `tests/`, `config/`, `Snakefile`: **nothing ever enforced it**, and **5 of the 8 had MOVED** (`occlusion_manifest.py` +46/−8, `occlus
266:> **⚠ D-04b-01 — A REAL DEFECT FOUND, DELIBERATELY NOT FIXED** (both modules are 0-diff-pinned): `bmi.AFR.PAGE.2019.GRCh37.tsv.bgz` stores POS as the **float string `5982778.0`**, and `int("5982778.0")` **raises** in `_canonical_key` in **both** `occlusion_present_rate_scan.py` and `drop_occlude
278:> **★ m3-07c LANDED** — authorized by Carter's **"Proceed"** in direct response to *"your explicit go is the only thing gating it."* NEW: `src/python/occlusion_present_rate_scan.py` (`scan_present_rate`; 6 RED → **6 passed**) + `src/python/drop_occluded_from_sumstats.py` (`drop_occluded_from_sum
297:> **✅ Frozen-contract gate CONFIRMED EMPTY:** `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` → empty; `condition_ld_matrix.py` → empty (m3-06 FROZEN/HELD, untouched); `content_verify_npz` body + the banded branch untouched. `exclude=None` yields a **byte-identical** 
301:> **⛔ NEXT = PAUSE. 07c NOT started** (Carter: "07b then PAUSE"). 07c = `occlusion_present_rate_scan.py` + `drop_occluded_from_sumstats.py`, and it populates the `traits_present`/`n_traits_present`/`n_traits_scanned` seam already DECLARED in `occlusion_manifest.STAGE_B_TRAIT_COLUMNS`. Unchanged:
311:> **⛔ NEXT = PAUSE. 07b/07c are UNBLOCKED but NOT AUTHORIZED** — Carter's standing instruction is "07a then PAUSE". 07b = production code (`occlusion_span_filter.py`, `--exclude` wiring in `run_native_ld_panel.py` + `aou_ld_panel.py`, `_PANEL_COLUMNS` += `n_dropped_occluded`); 07c = `occlusion_m
349:> **SESSION CLOSE 2026-07-07 (Carter stepping away). NC-State idle, all pushed (`46f3c27`).** The paragraphs below carry the full chain — this lead is the resume summary. **State:** m3-06 conditioning wave (999.1 §2-4) LANDED + independently verified, then HELD landed-but-not-trusted after Seth'
362:> - **§4 `write_conditioned_ld_npz.py`** (`f147041`) — banks a SEPARATE `{region}.conditioned.npz` with provenance keys (`n_zeroed`, `zeroed_pairs`, `nan_policy`, `psd_method`/`psd_lambda` placeholders filled at fit-time §5); raw `.npz` + `ld_npz_to_rds.R` FROZEN.
1601:| 260707-w78 | **Record the region-1 occlusion hinge check — resolves Seth's exclude-vs-flag "hinge fact" for the panel overlapping-variant policy (DOCS-only; read-only NC-State, no perimeter/spend/code; m3-06 stays HELD, `condition_ld_matrix.py` FROZEN, no loop contact).** Seth's review named 
1605:| 260715-sqe | **Resolved the m3-07b panel-column test-vs-test contradiction — the ONE open decision the 2026-07-15 close-session escalated as a Carter call.** Two tests contradicted and no implementation satisfied both: (a) `test_run_native_ld_panel.py::test_panel_columns_include_n_dropped_occ
1607:| 260715-u22 | **Closed BOTH blast-radius findings from the 2026-07-15 4-agent sweep — two PRE-EXISTING defects, TDD RED-first, one atomic commit each (different gates → independently revertible).** Neither was caused by quick-260715-sqe (`git diff --stat a76ebe5..HEAD -- src/` was EMPTY). **(1
1614:| 260804-rtc | **Landed the four autonomous `$0` correctness fixes the m3-04b blast radius cleared — every one of them a SILENT-failure class, and all four cheap now / expensive after an 11-day fire.** Ordered by Carter at a `/gsd-resume-work` after he chose the BLOCKER-1 remedy (see the DECISI
1618:| 260805-o7o | **Closed blast-radius findings H and I — the `m3-04c-BLAST-RADIUS.md:140` gate row "Trusting any AFR fine-map result" is now discharged** (A closed by `260805-23d`; H and I here). Carter chose this scope at a `/gsd-resume-work` and unfroze `run_susie_rss.R` for this task only. Ra
1620:| 260805-w7u | **Closed blast-radius finding E — the `m3-04c-BLAST-RADIUS.md:141` gate row "Any GWAS × QTL colocalization".** `qtl_coloc.smk` had ZERO crosswalk/resolver references, so `_qtl_coloc_ld_input` built the LEGACY `{ld_reference}/{ancestry}/{region}.rds` and fed that to `coloc::runsus
```
rc=0

#### `.planning/HANDOFF.json`

`$ grep -nE 'occlusion_manifest\.py|occlusion_present_rate_scan\.py|drop_occluded_from_sumstats\.py|ld_npz_to_rds\.R|pipeline\.schema\.yaml' .planning/HANDOFF.json | grep -iE 'frozen|freeze|pinned' | cut -c1-300`

```
18:    "⚠⚠ RETRACTION — the earlier claim 'All 7 pinned files 0-line diff vs bf16289' is FALSE. bf16289 appears in ZERO places across src/, tests/, config/, Snakefile (nothing ever enforced it) and 5 of the 8 files had MOVED: occlusion_manifest.py +46/-8, occlusion_present_rate_scan.py +154/-21, dro
118:    "▶ SR4-OPEN (a QUESTION, not a blocker) — FIVE files the project has been calling \"frozen\" were never enforced by anything AND have drifted: occlusion_manifest.py (+46/-8), occlusion_present_rate_scan.py (+154/-21), drop_occluded_from_sumstats.py (+97/-24), ld_npz_to_rds.R (+313/-62), pipe
```
rc=0

#### `.planning/ROADMAP.md`

`$ grep -nE 'occlusion_manifest\.py|occlusion_present_rate_scan\.py|drop_occluded_from_sumstats\.py|ld_npz_to_rds\.R|pipeline\.schema\.yaml' .planning/ROADMAP.md | grep -iE 'frozen|freeze|pinned' | cut -c1-300`

```
213:- [ ] m3-06-W6-ld-nan-psd-conditioning-PLAN.md — Wave 6 (999.1 §2-4 promotion; autonomous NCSU code, planned 2026-07-07): the AFR native-panel NaN conditioning MACHINERY under the posted OSF amendment (`tcujq`). **T1** — refactor the two r3 PSD fns (`psd_regularize_ridge`/`_eigclip`) into a shar
1077:   panel `.npz` contract frozen (`ld_npz_to_rds.R` unchanged).
```
rc=0

#### `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md`

`$ grep -nE 'occlusion_manifest\.py|occlusion_present_rate_scan\.py|drop_occluded_from_sumstats\.py|ld_npz_to_rds\.R|pipeline\.schema\.yaml' .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md | grep -iE 'frozen|freeze|pinned' | cut -c1-300`

```
57:> **(1) A CLAIM IN OUR OWN HANDOFF WAS FALSE.** "All 7 pinned files 0-line diff vs `bf16289`" — **retracted**. `bf16289` appears in **ZERO** places across `src/`, `tests/`, `config/`, `Snakefile`: there was **never any enforcement**. And **5 of the 8 had MOVED** — `occlusion_manifest.py` +46/-8, 
113:> **Nothing running. $0. No perimeter contact.** `origin == local`. Suite **584 passed / 31 skipped / 0 failed** (615 collected; baseline was 548). All seven frozen contracts 0-diff except `ld_npz_to_rds.R`, which Carter unfroze for one task. m3-06 stays HELD.
205:> **⚠ Plan wrong twice (both fixed):** `envs/m3-r-ld.yml` lacked pandas (added `pandas>=2.2` there, NOT to `python_stats.yml` which backs a dozen built rules); `pipeline.schema.yaml` is `additionalProperties:false` so the new `occlusion_lockstep:` block needed a schema entry or every Snakemake r
217:> **★ m3-07c LANDED** (`c475da7` T3 + `ed3e122` T4) — authorized by Carter's **"Proceed"** in direct reply to *"your explicit go is the only thing gating it."* NEW: `src/python/occlusion_present_rate_scan.py` (`scan_present_rate`; 6 RED → **6 passed**) + `src/python/drop_occluded_from_sumstats.p
233:> **m3-07b LANDED** (`7734725`/T1 + tag `m3-07b-W7-T1`; `0473b6a`/T2 + tag `m3-07b-W7-T2`; `a76ebe5` docs). NEW: `src/python/occlusion_span_filter.py`, `src/python/occlusion_manifest.py`. MODIFIED: `aou_ld_panel.py` (`build_plink_ld_command(exclude=)`) + `run_native_ld_panel.py` (`process_region
249:> **Nothing running server-side, $0. Local HEAD `8f36fdf` = 2 commits AHEAD of origin `bd4d50a`, HELD unpushed ON PURPOSE (Carter order = hold-then-push-all-four).** THIS SESSION (docs-only, read-only, no perimeter): ran Seth's exclude-vs-flag **hinge check** — the panel↔sumstats join is `(CHR,P
252:> **(A)** m3-06-W6-ld-nan-psd-conditioning (999.1 §2-4) LANDED via autonomous plan→execute per Carter's `--auto --chain`, structured as a WAVE-in-m3 (his call, not a standalone phase): promote `20e3adc` → planner `205b03e` → plan-checker PASS → executor 6 commits HEAD `f147041` (`psd_utils.R` by
```
rc=0

#### `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`

`$ grep -nE 'occlusion_manifest\.py|occlusion_present_rate_scan\.py|drop_occluded_from_sumstats\.py|ld_npz_to_rds\.R|pipeline\.schema\.yaml' .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md | grep -iE 'frozen|freeze|pinned' | cut -c1-300`

```
```
rc=0

#### `.planning/amendments/AOU-LD-PIPELINE.md`

`$ grep -nE 'occlusion_manifest\.py|occlusion_present_rate_scan\.py|drop_occluded_from_sumstats\.py|ld_npz_to_rds\.R|pipeline\.schema\.yaml' .planning/amendments/AOU-LD-PIPELINE.md | grep -iE 'frozen|freeze|pinned' | cut -c1-300`

```
```
rc=0
### The SR4-OPEN question VERBATIM from `deferred-items.md`

`$ sed -n '989,1035p' .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`

```
## ⚠ SR4-OPEN — FIVE files `HANDOFF.json` calls "frozen at `bf16289`" have MOVED. A QUESTION FOR CARTER, deliberately NOT answered.

**Logged:** 2026-08-06 (`quick-260806-sr4`). **Status: OPEN — registered, NOT
resolved either way.**

`.planning/HANDOFF.json:14` states *"All 7 pinned files 0-line diff vs
`bf16289`"*. **That claim is FALSE for 5 of 8 files.** MEASURED at `1b5b8c6`
with `git diff --numstat bf16289 HEAD`:

| File | Diff vs `bf16289` | Last touched | Handled |
|---|---|---|---|
| `src/python/plink_ld_to_npz.py` | **0** | 2026-07-03 | ✅ **GATED** |
| `src/python/condition_ld_matrix.py` | **0** | 2026-07-07 | ✅ **GATED** |
| `src/python/occlusion_span_filter.py` | **0** | 2026-07-15 | ✅ **GATED** |
| `src/python/occlusion_manifest.py` | +46 / −8 | 2026-08-04 (`bf963df`) | ⚠ **MOVED — not gated** |
| `src/python/occlusion_present_rate_scan.py` | +154 / −21 | 2026-08-04 (`fac9a93`) | ⚠ **MOVED — not gated** |
| `src/python/drop_occluded_from_sumstats.py` | +97 / −24 | 2026-08-04 (`bf963df`) | ⚠ **MOVED — not gated** |
| `src/scripts/ld_npz_to_rds.R` | +313 / −62 | 2026-08-05 (`57b381f`) | ⚠ **MOVED — not gated** |
| `src/snakemake/schemas/pipeline.schema.yaml` | +119 / −0 | 2026-08-06 (`2563451`) | ⚠ **MOVED — not gated** |

**It is worse than it looks.** `bf16289` appears **nowhere** in `src/`, `tests/`,
`config/`, `Snakefile` or `scripts/` — until `quick-260806-sr4` there was
**literally zero enforcement** of any of these. The "freeze" was a per-task hand
check, and that ritual had been **reporting a claim that is false for five of
eight files**.

**Why three were gated and five were not.** `AUTH-SR4-EXTEND` covers only files
that are **measured 0-diff** against the pin. Gating a file that changed three
times in the last three days would manufacture exactly the nuisance-repin
timebomb the rescope exists to remove, and **declaring a moving file frozen is a
DECISION, not an inference.** So the three genuinely-unmoved modules became real
gates and the other five were deliberately left alone. A permanent test
(`test_the_handoff_frozen_claim_is_recorded_as_partly_false`) asserts the five
are **out** of the pinned set, so a future sweep cannot "helpfully" add them back
without a decision.

**THE QUESTION FOR CARTER — not answered here.** For each of the five: were they
**frozen and have since drifted** (in which case something was changed that
should not have been, and the drift needs review), or were they **never actually
frozen** (in which case `HANDOFF.json:14` should be corrected and they should
stop being described as pinned)? These are different problems with different
remedies, and choosing between them is a call about intent that no agent can
make from the diff alone.

**Nothing is blocked on the answer.** The three real gates are live either way.
```
rc=0

### LIVE current-state assertion vs HISTORICAL dated block

This repo's narrative files carry dated session blocks prefixed `>`, which are
HISTORY and correctly describe what was true when written. A residual
CORRECTION SITE is a claim NOT inside such a block -- i.e. a current-state
assertion. Classified mechanically by the `>` prefix rather than by reading.

`$ awk -F: 'NR==FNR{next}1' /dev/null /dev/null; for L in 15 17 39 266 278 297 301 311 349 362; do printf '%s: ' $L; sed -n "${L}p" .planning/STATE.md | cut -c1-3 | sed 's/^>.*/HISTORICAL (> block)/; s/^[^H].*/LIVE (no > prefix)/'; done`

```
15: LIVE (no > prefix)
17: LIVE (no > prefix)
39: LIVE (no > prefix)
266: HISTORICAL (> block)
278: HISTORICAL (> block)
297: HISTORICAL (> block)
301: HISTORICAL (> block)
311: HISTORICAL (> block)
349: HISTORICAL (> block)
362: HISTORICAL (> block)
```
rc=0

The two LIVE sites in full, with context:

`$ sed -n '1,20p' .planning/STATE.md`

```
---
gsd_state_version: 1.0
milestone: v3.1.2
milestone_name: milestone
status: "m3-07b LANDED — the occlusion span-filter + provenance manifest are REAL CODE (7734725/T1 + 0473b6a/T2; both tags on origin). Full tests/m3 47F→16F (32 newly green); 15 of 16 remaining = 07c's unbuilt modules (expected). Frozen contracts 0-line diff across the whole session. m3-07a COMPLETE + UAT-VERIFIED 11/11. OSF gate CLEARED + fully recorded (GUID trsx5; append-only verified; NO open follow-ups). ⚠ **DECIDE FIRST:** exactly one real red = a TEST-vs-TEST contradiction (07a RED requires n_dropped_occluded in _PANEL_COLUMNS vs pre-existing test_panel_tsv_append_resume_safe pinning 8 exact columns) — a Carter call, deliberately unresolved; 1-line fix proposed in HANDOFF.json. **Then:** Carter's go for 07c. ✅ ALL PUSHED — origin == local == a76ebe5, all 5 tags on origin; remote is SSH (no PAT). No AoU loop re-fire (loop STOPPED, .npz 0/276; 07c + a region-1 validation are the precondition). m3-06 HELD, condition_ld_matrix.py FROZEN."
stopped_at: "m3-07b EXECUTED + LANDED 2026-07-15 (7734725/T1 span-filter + 0473b6a/T2 manifest + a76ebe5 docs; tags m3-07b-W7-T1/T2 pushed). Full tests/m3 16 failed/394 passed/31 skipped (from 47F/363P/31S = 32 newly GREEN). 15 of the 16 remaining are 07c's unbuilt modules (ModuleNotFoundError: drop_occluded_from_sumstats / occlusion_present_rate_scan) = EXPECTED. NEXT (in order): (1) ⚠ DECIDE the ONE real red — a TEST-vs-TEST contradiction: the 07a RED test_panel_columns_include_n_dropped_occluded:1589 requires n_dropped_occluded in _PANEL_COLUMNS, while the PRE-EXISTING test_panel_tsv_append_resume_safe:392 pins list(df.columns) to EXACTLY 8 columns without it; _append_panel_row_local writes columns=_PANEL_COLUMNS → 9 columns → the pre-existing test fails. It's an OMISSION in the 07a RED (precedent 1a9d170 updated the column-list assertion in the same commit as the prior column). Proposed 1-line fix, NOT applied: add n_dropped_occluded at index 7 of that expected list. Do NOT drop the column (fails the 07a RED + discards the OSF-pre-registered occlusion provenance). The executor correctly refused to edit either test — do not let an agent 'fix' this by weakening the RED. (2) THEN 07c on Carter's explicit go. Do NOT start 07c unprompted."
last_updated: "2026-08-04T13:15:00.000Z"
# m3-07b EXECUTED 2026-07-15 (see the LATEST section block below — that block is authoritative):
# T1 span-filter 7734725 + tag m3-07b-W7-T1; T2 manifest 0473b6a + tag m3-07b-W7-T2; both PUSHED (origin == local).
# Full tests/m3 16 failed / 394 passed / 31 skipped (baseline 47F/363P/31S) -> 32 newly GREEN, 1 newly RED.
# 15 of the 16 remaining = the 07c T3/T4 suites (ModuleNotFoundError, EXPECTED, out of 07b scope).
# ⚠ 1 BLOCKER REPORTED, NOT RESOLVED: test_panel_tsv_append_resume_safe:392 (exact 8-col panel TSV) contradicts
# the 07a RED test_panel_columns_include_n_dropped_occluded:1589 — no impl satisfies both; test NOT edited per the
# standing instruction; proposed 1-line companion fix (precedent 1a9d170) is in the m3-07b SUMMARY awaiting Carter.
# Frozen contracts byte-unchanged (plink_ld_to_npz.py / ld_npz_to_rds.R / condition_ld_matrix.py all git-diff EMPTY).
# 07c NOT started (Carter: "07b then PAUSE"). No perimeter contact, no loop re-fire, no OSF edit.
last_activity: "2026-08-04 (LATEST — SESSION CLOSE) — ⛔ m3-04c HALTED after the m3-04b BLAST-RADIUS sweep (4 independent read-only investigators + orchestrator verification; $0, NC State, no perimeter, ZERO source drift). Resumed via /gsd-resume-work --auto --chain and DELIBERATELY DID NOT EXECUTE m3-04c: its headline must_have is FALSE AS SPECIFIED. BLOCKER-1 (PRE-EXISTING, needs CARTER): {input.ld_matrix} is never referenced in run_finemap's shell block — run_susie_rss.R gets only --ld-dir + --region and rebuilds file.path(ld_dir, ancestry, id.rds) at :124-127; ancestry is 'AFR', NEVER 'AFR_aou'; no rule promotes AFR_aou/*.rds into AFR/; on a miss it falls SILENTLY to an identity matrix (:472-474). PROVEN EMPIRICALLY — with the AoU panel present on disk, resolve_ld_path returns AFR_aou/m2_region_00067.rds (exists) while SuSiE opens AFR/FTO_16q12.rds (absent). The crosswalk is NECESSARY but NOT SUFFICIENT; the 2026-08-03 diagnosis verified 3 ways, all at the DECLARATION layer. Carter picks: --ld-file thread (RECOMMENDED) / promote-symlink rule / per-ancestry ld_dir. BLOCKER-4 (NEW, autonomous $0, land BEFORE the fire): assemble_occlusion_catalog.py:352-359 ignores EVERY excludelist and stamps stage_a_manifest when the rollup is merely NON-EMPTY, not COMPLETE; run_native_ld_panel.py:821-831 already swallows the exception that creates excludelist-only regions; no completeness check vs 276 exists → orphaned variants wearing a clean provenance stamp. BLOCKER-2/3 (block the MERGE): test_occlusion_lockstep_wiring.py:410 asserts the exact string T1 must replace while its own docstring says m3-04c changes it (proven: 1F/13P on the plan's verbatim edit), with the real params.region_id pin at :406 immediately above it = a bait; and m3-04b's +48 lines make EVERY finemap.smk line number in the m3-04c plan stale, its do-not-touch guard now pointing at the block to EDIT. m3-04b ITSELF IS SOUND, no revert: non-AFR byte-identity empirically true across every instantiated combination + all 10 schema-passing permutations behind 2 independent barriers (Track-A/EUR numerics cannot move); both inputs move together 36/60 with no half-wired job; strictly additive DAG (178 vs 162 = exactly the 16 new jobs); mirrors format-faithful; alignment by identifier not position (which keeps BLOCKER-1 a detectable over-exclusion, not corruption); 444P/31S/0F non-tautological; all 7 pinned files 0-line diff. Independently reproduced the m3-04c crosswalk oracle 12/12 EXACTLY and verified every factual claim in its <interfaces> — that plan's FACTS are sound, its PREMISE is wrong. D-04b-01 extent MEASURED: one file (bmi.AFR.PAGE) but 100% of its 17,195,956 rows, nothing else in the corpus malformed; goes LIVE the moment BMI-AFR is re-harmonized to bmi.AFR.tsv.bgz. Report = .planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md (6ff5d5f, pushed). Memory lesson baked: feedback_declared_input_is_not_the_read_path. Nothing running, $0, origin == local == 6ff5d5f. PRIOR 2026-07-15 (SESSION CLOSE) — m3-07b LANDED: the occlusion span-filter + provenance manifest are REAL CODE (7734725/T1 + 0473b6a/T2 + a76ebe5 docs; tags m3-07b-W7-T1/T2 both on origin). Created src/python/occlusion_span_filter.py + src/python/occlusion_manifest.py; modified aou_ld_panel.py (build_plink_ld_command exclude=) + run_native_ld_panel.py (process_region reorder, n_dropped_occluded split). Full tests/m3 47F/363P/31S → 16F/394P/31S = 32 newly GREEN; 15 of the 16 remaining are 07c's unbuilt modules (EXPECTED). Frozen contracts (plink_ld_to_npz.py / ld_npz_to_rds.R / condition_ld_matrix.py) VERIFIED 0-line diff across the ENTIRE session. GPFS hazard did NOT recur on 07b. ⚠ EXACTLY ONE real red = a TEST-vs-TEST CONTRADICTION needing a CARTER CALL, deliberately NOT resolved: the 07a RED (test_panel_columns_include_n_dropped_occluded:1589) requires n_dropped_occluded in _PANEL_COLUMNS, but the PRE-EXISTING test_panel_tsv_append_resume_safe:392 pins the panel TSV to EXACTLY 8 columns without it; _append_panel_row_local writes columns=_PANEL_COLUMNS so the TSV now has 9 → the pre-existing test fails. Diagnosis = an OMISSION in the 07a RED (precedent 1a9d170 added the prior panel column RED-first AND updated the column-list assertion in the SAME commit). Proposed 1-line fix (NOT applied): add n_dropped_occluded at index 7 of the expected list. Do NOT instead drop the column — that fails the 07a RED and discards the per-region occlusion provenance osf.io/az52u pre-registers. The executor correctly REFUSED to edit either test. BEFORE executing, 07b's PLAN was RECONCILED to 07a's corrected RED (f3b79fe) — it contradicted it 3 ways (edges as list[dict] → unhashable → set(edges) TypeError; a disjoint/second-order edge the RED forbids; occlusion_order (direct|second_order) the fix made optional/direct-only) = the SAME root cause the blast-radius traced, living in the plan. 07c NOT started (Carter's '07b then PAUSE' honored). Nothing running; $0. PRIOR SAME-DAY (2026-07-15) — m3-07a EXECUTED + COMPLETE + UAT-VERIFIED 11/11 (46dd661), then the blast-radius sweep FIXED a defective RED CONTRACT (a1e8693) BEFORE 07b was built against it: BLOCKER = occlusion_order demanded 'second_order' for snpC, INVERTING the byte-verified verdict (pair 3 IS a direct ref_span_overlap) and underivable from a genotype-free Stage A → the only route to green was HARDCODING position 5922718 = a false provenance label across all 276 regions (T-m3-07a-02 realized, arrow reversed — the test would have DRIVEN the wrong impl); HIGH = the gated oracle compared bp against ROW INDICES so it could never pass a correct detector; 3 MEDIUMs (strict-left < vs <=, multi-occluder set()-hidden duplicates, whole-key egress guard) + an untested producer→consumer seam. PUSH UNBLOCKED PERMANENTLY: Carter registered the node's ~/.ssh/id_rsa on GitHub, remote switched HTTPS→SSH, no PAT ever again; LESSON — `git push` does NOT push tags, and 2 tags including the OSF GATE RECORD were stranded local-only on the lossy store. OSF GUID CAPTURED = trsx5 (osf.io/az52u/files/trsx5); append-only commitment VERIFIED (trsx5 1 revision, tcujq still 1 revision unmodified → separate new file, NOT a re-version → NO posting deviation); tcujq was offered for that slot and REFUSED (it's the 2026-07-04 amendment the update WITHDRAWS). origin == local == a76ebe5, all 5 tags on origin. PRIOR (same day, superseded detail) — Resumed via /gsd-resume-work off the 2026-07-10 HANDOFF. (1) CLOSED the flagged reconciliation: 07a Task 1 named a PLACEHOLDER amendment file/tag that NEVER EXISTED and its verify grepped 3 strings the real Carter-authored posted doc lacks ('never zeroing', 4543dcf4, 42d70167) — reconciled the PLAN to the posted reality rather than editing the amendment (editing it would diverge the repo copy from the bytes on OSF; recorded as threat T-m3-07a-03), marked Task 1 PRE-CLOSED, retargeted the verify to checks the real artifacts satisfy + re-verified BOTH science body anchors where they actually live (tail -c 5012 == 4543dcf4…, tail -c 5247 == 42d70167…) → GATE_CONFIRMED_OK (e10c893). (2) GPFS object-store loss RECURRED (3rd time): 13 loose blobs lost, commit failed 'invalid object / Error building trees'; ALL 13 recovered via the guarded hash-object -w recipe (every one hash-matched its worktree file, 0 unrecoverable). git fsck also shows 194 pre-existing broken links in OLDER (already-pushed) history — the push set itself is INTACT (71 objects, 0 missing). (3) Wave 0 RED landed 296157a + tag m3-07a-W7-T-WAVE0 via gsd-executor (adapted planner→executor pattern). Independently verified: zero collection errors, call-time ModuleNotFoundError, full tests/m3 44 failed/363 passed/31 skipped with 44==38+6 == exactly the new tests. KEY DEVIATION accepted: _MockPlink gained nan_snps because the 'npz has NO NaN' test would otherwise pass GREEN with zero impl (vacuous) — it now models the real mechanism, and the driver fails through the REAL NaN guard naming rows [1,3,5,8,10] == exactly the 5 occluded fixture rows (fixture geometry confirmed end-to-end, not merely asserted). ⚠ OPEN: 10 commits UNPUSHED — push BLOCKED on Carter's fine-grained PAT (a stale credential.helper=cache gave the documented misleading 'Invalid username or token'); OSF file GUID still uncaptured (non-blocking). PRIOR 2026-07-08 SESSION CLOSE — exclude-vs-flag RESOLVED = exclude-in-lockstep + provenance manifest (Seth-endorsed; policy doc 8f36fdf byte-verified 42d70167…/5247 B); the w78 hinge check found occluded SNP rs182965575 PRESENT in 7/9 AFR sumstats (Seth's 'present' case); NaN→0 DEAD, panel-only-exclude UNSAFE; HOLD-THEN-PUSH-ALL-FOUR pending the geometry-verdict base64 (local 8f36fdf is 2 ahead of origin, unpushed on purpose); m3-06 HELD, condition_ld_matrix.py FROZEN, loop NOT re-fired. PRIOR 2026-07-07 (LATEST) SESSION CLOSE - m3-06 HELD landed-but-not-trusted; the NaN mechanism is RESOLVED 6/6 = overlapping-deletion occlusion (2×2 genotype tables + full-.bim REF-span geometry; 5 direct + 1 second-order, 0 same-position/mergeable) → NaN→0 definitively dead, fix = exclude-occluded / flag-locus WITH PROVENANCE, likely an UPSTREAM panel-build span-filter for all 276 regions. ⚠ ONE open in-repo action: commit the geometry VERDICT artifact (anchor SHA 4543dcf4 / 5012 B) — BLOCKED, my chat-paste reconstruction was 142 B short (table formatting lost) → refused to commit unverified → NEED a base64/fenced transfer. The scientific-review MEMO is committed byte-verified (3516c18). Loop-hash typo fixed (loop ran on 2d23d67, not the nonexistent 2d43d67); loop RUNNING-vs-STOPPED UNRESOLVED (Seth: stopped/PID 5170 killed; needs an in-perimeter data-layer check). 3 Carter policy calls pending (exclude-vs-flag / upstream-vs-per-region / narrow amendment-update), all checked vs the chr:pos:ref:alt harmonization key. All pushed (46f3c27); NC-State idle. PRIOR 2026-07-07 - Recorded the region-1 2×2 diagnostic RESULT + a harmonization-key finding in the SCIENTIFIC HOLD block. The 2×2 (egress-clean, loop untouched) CONFIRMED the mechanism: every pair has one variant monomorphic on the pairwise-complete subset (carriers ~100% missing at the partner) → r is genuinely NULL, no 'real r' to substitute → NaN→0 is DEFINITIVELY dead. Seth's REFINEMENT: 5/6 pairs are directionally asymmetric (occluder = longer indel/deletion covering a SNP partner) = an overlapping-deletion artifact, NOT a duplicate → bcftools norm -m + fixes ONLY pair 5 → fix = normalize true splits + overlap-detection to exclude/flag the occluded variant. I VERIFIED the harmonization-key coupling NC-State: the panel↔sumstats join is on SNP_ID=chr:pos:ref:alt (ld_npz_to_rds.R + refit_sh2b3_psd_regularized.R:106,137 + snp_id_bridge.R) → normalizing the panel changes the join key → EXCLUDE-occluded is the join-safest option. NEXT (egress-safe, NOT loop-gated): full untruncated .bim records for the ~11 variants (Seth drafting) → exact overlap geometry → Carter's policy call (normalize+decompose vs exclude-occluded vs flag-locus) checked vs the harmonization key. m3-06 STAYS held; raw-panel NaN-raise stays. PRIOR 2026-07-07 - Completed quick-260707-n11 (DOCS-only): committed Seth's NaN-conditioning scientific-review memo in-repo at .planning/amendments/m3_nan_conditioning_scientific_review.md (byte-verified full-body SHA-256 e82201147c / 7364 B == Seth's anchor; self-locating header note prepended). It's the durable record of WHY m3-06 is HELD landed-but-not-trusted: the NaN mechanism is mis-identified — pairwise-monomorphism is ~1e-947..1e-3729 improbable at F_MISS≤0.05/MAF 0.005-0.02 → correlated missingness at co-located records (index-adjacent, 8-52 bp) = likely variant-representation artifact; NaN→0 is a directionally-wrong fill for high-LD neighbors. GATE: the region-1 2×2 diagnostic must resolve the mechanism before any conditioned region feeds a fit. Reconciled the existing SCIENTIFIC HOLD block (21a5642) instead of duplicating (memo pointer→in-repo path + 5-8bp→8-52bp). Do-NOTs honored: OSF amendment/coverage flag/tag UNTOUCHED, read_square_bin NaN-raise intact, condition_ld_matrix.py FROZEN, no OSF re-post. Two paste blocks in flight: the region-1 2×2 diagnostic (→AoU browser agent, egress 6-row JSON only) + this memo commit (done). PRIOR 2026-07-07 - LANDED m3 wave m3-06-W6-ld-nan-psd-conditioning (999.1 §2-4, autonomous plan→execute per Carter's --auto --chain, structured as a wave-in-m3 not a standalone phase). Chain: promote 20e3adc → gsd-planner 205b03e → gsd-plan-checker PASS → gsd-executor 6 commits HEAD f147041. §2 psd_utils.R (47707ad) extracts psd_regularize_ridge/_eigclip into a shared util that refit_sh2b3 sources — Track-A byte-identity VERIFIED 16/16 identical()=TRUE (frozen golden 335f944a + verbatim ref), r3/EUR numerics UNCHANGED; §3 condition_ld_matrix.py (ccca5b8) memory-bounded NaN→0 to the amendment exactly (topology branch, 0.05%×n_var ceiling→RAISE, provenance; region-1 n_zeroed_pairs==6); §4 write_conditioned_ld_npz.py (f147041) separate {region}.conditioned.npz with provenance keys. Independently verified: full tests/m3 360 passed/30 skipped (336+24 new), frozen contracts (plink_ld_to_npz.py/run_native_ld_panel.py/ld_npz_to_rds.R) git-diff-EMPTY, byte-identity re-run exit 0. §5-6 REMAIN PARKED (loop-gated). No perimeter access; AoU loop untouched. PRIOR 2026-07-04 - Completed quick-260704-0uf (DOCS + tag): recorded the POSTED AFR native-panel NaN→0 + PSD OSF amendment (999.1 OSF gate). Seth posted it — OSF file tcujq on az52u (https://osf.io/az52u/files/tcujq), authoritative UTC 2026-07-04T04:14:46.635031Z; body Date field 2026-07-03 = a DISCLOSED 1-day date-vs-post-instant deviation (not re-posted). Committed the byte-faithful FILLED amendment (.planning/amendments/osf-amendment-afr-native-ld-nan-psd-2026-07-03.md, SHA-256 VERIFIED vs Seth's anchors: content-after-header 1a25a7ba/12672 B + posted-body 43248aff/8332 B; self-locating header note prepended) + a dated .planning/osf_deviations.md entry + the coverage flag D-AFR-NANPSD-OSF-COVERAGE: COVERED at 2026-07-04T04:14:46Z → 999.1 steps 2-6 UNBLOCKED (conditioning may proceed under /gsd-plan-phase; NO loop re-fire until §1-6 land). PRECEDENCE holds (gate 0f3c68b committer-date 03:45:29Z precedes the +29-min post + all conditioning-output commits, none exist). Tagged AFR-NANPSD-OSF-AMENDMENT-POSTED-2026-07-04 on 0f3c68b. PRIOR 2026-07-04 - Completed quick-260703-wx2 (DOCS-ONLY): expanded ROADMAP 999.1 backlog with Seth's resolved OSF finding + 6-step work breakdown (status stays parked, NOT promoted). Resolved: osf-amendment-r3-2026-05-04.md is EUR-only (1000G Phase 3 EUR panel, SH2B3+4 EUR regions; defers AFR to Track B/All-of-Us EUR) → it does NOT cover the AFR native panel or a NaN→0 step → 999.1 needs a NEW OSF amendment (Carter posts; agent DRAFTS) = the TRUE blocker on promotion; the PSD methods (psd_regularize_ridge/_eigclip) are reusable but their pre-registration coverage is not. Appended a '#### 999.1 design detail' subsection under the existing entry (stub intact): reuse the two PSD fns via a shared psd_utils.R (no 3rd impl); NaN topology (12 NaN/11 rows/0 fully-NaN → isolated pairs → NaN→0 + PSD per-region provenance, NOT a variant drop; branch on topology); NaN→0-first / PSD-on-submatrix-second ordering (full 102421² eigen ~195 GiB > 120 GB VM); fine-mapping caveats; 6-step work breakdown for /gsd-plan-phase when promoted; do-NOTs. Committed only ROADMAP.md + STATE.md, explicit paths. No code, no re-fire, no promotion. PRIOR 2026-07-04 - Completed quick-260703-vk9 (Seth Defect 1 — snplist-read RACE guard in run_native_ld_panel.py: a bare read_text() on {out_prefix}.snplist raced plink's flush → empty snplist → 0 retained ids → a false n_var mismatch = the live region-1 'window .bim has 0 rows' error). Fix (3 edits, run_native_ld_panel.py ONLY): (A) _needs_retained_subset skips the snplist∩.bim intersection when --mac dropped nothing (bin==raw, the observed AFR regime); (B) _retained_window_bim gains expect_nonzero → a bounded retry on the snplist read mirroring _window_bim_n_var_retry_on_zero (loud WARN on recovery; persistently-empty still returns [] → the caller's byte-identical n_var mismatch still fires — nothing loosened); (C) conditional square caller. TDD RED→GREEN, tests/m3/test_defect1.py (3 cases); full tests/m3 336 passed / 30 skipped (baseline 333+3). Did NOT touch o0m's test_plink_ld_to_npz.py/test_nan_guard.py/test_gate.py or plink_ld_to_npz.py. ⚠ CODE ONLY — NOT on the running VM (2d3d67); the loop is STILL RUNNING and MUST NOT be re-fired. Carry-forwards (non-blocking): NaN→0 + PSD downstream policy (backlog 999.x); mechanism framing softened to 'pairwise-undefined r among clustered low-MAF variants (0/0 on a pair's complete-sample intersection), NOT a plink bug'. PRIOR 2026-07-03 (LATEST) - Completed quick-260703-o0m (Seth Defects 3+4, NC-State-side, CODE ONLY): (D3) read_square_bin now raises a NaN-SPECIFIC error naming the culprit variant row(s) BEFORE the symmetry check (new block-wise _has_any_nan_blocked + nan_variant_indices ranked-by-NaN-count, robust to the real diagonal-1.0 / sparse fire-#3 fingerprint where .all(axis=1) yields []; was the misleading 'not symmetric'); (D4) opt-in --fail-fast RegionGateError gate in run_native_ld_panel (default-off = resume-safe continue byte-behaviour-identical). TDD RED→GREEN, 4 commits 28c70ff/b57d31e/ebceb43/12b86d6; Carter-approved read_square_bin do_not EXCEPTION (diagnostic-only, never loosens the diagonal/symmetry/OOM checks). ⚠ NOT on the running VM (2d23d67): the loop is STILL RUNNING server-side and MUST NOT be re-fired — Seth Defects 1 (snplist∩bim=0) + 2 (true NaN source) root-cause pending in-perimeter diagnostics. PRIOR 2026-07-02T20:20Z - 🔥 LOOP FIRED + RUNNING on the AoU VM. Carter fired step 4; the 276-region AFR native-plink LD loop is RUNNING server-side on the drop-monomorphic + hardened code (2d23d67, origin==local, pushed), VM AoU_Jupyter_ComputeEngine_20260626b (n1-standard-32/120GB), nohup + timeout 312h, run log ~/native_ld_loop.log; region 1 computing = the gate (~2.5h to bank). Steps 1-3 (pull 2d23d67 + re-gate grep write-snplist/n_dropped_monomorphic + .bim col-2 uniqueness awk) passed pre-fire. GATE region 1: PASS (npz 0->1, panel status==ok, n_var<102,421, n_dropped~11 logged, no 'not symmetric'/Killed/dmesg-OOM) -> loop continues to 276 (~11 days, 2-3d check-ins); FAIL -> AoU agent kills + reports ('not symmetric'=residual NaN; 'ambiguous variant id'=H1 dup-id assert => investigate export). Liveness = bucket .npz count -> 276. Do NOT restart kernel; STOP-on-complete (stop != delete) at 276 -> native-panel-recorded -> NCSU reconstructs panel TSV -> m3-04 REPLAN. This session (all pushed, 321/30 green): fire #3's region-1 failure RE-DIAGNOSED from a mis-called 'transient' to the REAL monomorphic-NaN symmetry failure (read_square_bin RAISES on the intact .ld.bin; 12 NaN across 11 monomorphic rows); DECISION drop MAC=0; FIX quick-260701-qcy (--mac 1 --nonfounders --write-snplist + _retained_window_bim snplist threading; 587c3d4/c56c715) + HARDENING (H1 dup-id assert + H2 n_dropped_monomorphic provenance; 1a9d170/ed9cfd4); 4-dim Fable-5 blast-radius + verifier 7/7 CLEAN (downstream .rds aligns by variant ID). PRIOR 2026-07-02 - DROP-MONOMORPHIC FIX LANDED+GREEN (quick 260701-qcy): the SQUARE plink LD command now emits --mac 1 --nonfounders --write-snplist so plink drops MAC=0 (monomorphic-in-AFR) variants BEFORE --r -> no 0/0->NaN LD -> read_square_bin's symmetry check passes; new reusable _retained_window_bim(raw_window_bim, snplist) intersects the raw in-window .bim with the plink .snplist in snplist(==.ld.bin) order so per-region n_var==retained + the .npz variant list aligns. T1 @ 587c3d4 (RED) + T2 @ c56c715 (GREEN); full tests/m3 green (baseline 309 + 5 new). The 27af416 transient guard PRESERVED (still the raw-window producer; only the cross-check operand moved to the retained count); n_var mismatch ValueError byte-identical; read_square_bin/load_bim/content_verify_npz/banded/resume UNCHANGED. NOT yet pushed. RE-FIRE PENDING: push origin -> AoU git pull >= c56c715 on the SAME n1-standard-32 (NO respec) -> re-gate (grep write-snplist) -> REGION-1-ONLY gate (read_square_bin passes, status==ok, n_var slightly < 102,421) -> ONLY THEN the full 276. PRIOR 2026-06-30 (was-LATEST) - FIRE #3 (n1-standard-32/120GB, 1b45d43) PROVED both OOM fixes (NO dmesg OOM on region-1 .npz convert + content_verify_npz) but region 1 hit a NON-REPRODUCIBLE TRANSIENT cohort-.bim short-read -> status=error 'window .bim has 0 rows' -> banked 0/276 (resume-safe; we STOPPED it at region 1 to investigate). ~6 read-only dig rounds RULED OUT every static cause (src md5 e99fd817==committed; _window_bim_n_var chr-agnostic + byte-identical a5a5f9f->1b45d43; manifest md5 matches, chr int64/no-NaN, chr=int 1; same interpreter/pandas 2.3.2; .bim full+stable mtime Jun 27; EXACT driver path REPLAYS 102421==102421; float-chrom mechanism proven-possible but ruled out). RETRY GUARD landed+green (quick 260630-rn4: reusable _window_bim_n_var_retry_on_zero re-reads .bim 3x when square window=0 but bin>0, WARN on recovery, byte-identical raise on persistent 0; T1 bba9cf8 + T2 27af416; full tests/m3 309/30). RE-FIRE PENDING on the guarded code: PUSH origin (deferred) -> AoU git pull >=27af416 on the SAME n1-standard-32 (NO respec - OOM concern resolved) -> re-gate -> re-fire same loop_command. Liveness = bucket .npz -> 276. PRIOR 2026-06-29 (LATEST) - BLAST-RADIUS on the .npz OOM fix (3eac803) CAUGHT A SECOND OOM HEAD: content_verify_npz (run_native_ld_panel.py:228, the in-process D-M3-10 gate run right after the convert) reloads the full .npz and re-runs the SAME unbounded np.allclose(ld, ld.T) -> ~4x matrix ~156 GiB at n_var=102,421 > the 128 GB re-fire VM -> would OOM region 1 AGAIN, one function later. The 260629-2im fix alone was INSUFFICIENT. FIXED @ ff9e66f (quick 260629-402): square -> reuse pln._is_symmetric_blocked; banded (same class, off-path) -> new pln._strict_upper_is_zero_blocked (block-wise np.triu k=i+1); reason strings byte-identical; TDD failing-first; targeted 48 passed, full tests/m3 305 passed/30 skipped (>=302). Both square convert->verify OOM heads now bounded (region-1 peak ~40 GiB). Re-fire now needs git pull of ff9e66f (not just 3eac803). 4-investigator sweep ALSO verified: predicate provably equivalent (927 cases, 0 disagreements), .npz/callers/resume all safe; non-blocking notes = SIGKILL writes no panel row + peak_ram_gib measures the plink child not the convert -> watch bucket .npz count + grep Killed/137. PRIOR 2026-06-29 (earlier) - RE-FIRED LOOP (PID 6577) OOM-KILLED on region 1's .npz convert, banked 0/276 AGAIN (different bug — the chr-prefix fix is PROVEN: region-1 plink finished + emitted the 102,421-var .ld.bin). Root cause: read_square_bin's np.allclose(m, m.T) symmetry check builds several full n_var^2 float32 temporaries (~39 GiB each) on top of the 39 GiB matrix -> >64 GiB peak -> OOM (savez is NOT the killer, it streams chunked). FIXED via _is_symmetric_blocked blocked check (commit 3eac803; tests/m3 test_plink_ld_to_npz 17 passed, full suite 302 passed/30 skipped; quick 260629-2im). Carter STOPPED the VM (idle-billing halted, stop != delete). DECIDED: re-fire on n2-highmem-16 (128 GB) for headroom. Re-fire = push origin (verify tip==HEAD) -> agent git pull 3eac803 -> UI respec to highmem -> pre-flight region-1 window ~102,421 -> re-fire from region 1 -> proof .npz 0->1 + df flat. PRIOR 2026-06-28 ~05:50Z - LOOP RE-FIRED on FIXED code (PID 6577, a5a5f9f). The first fire (PID 4237) banked 0/276 in ~17h: _window_bim_n_var compared the chr-prefixed cohort .bim contig (chr1) against the bare-numeric ld_regions.tsv chr (1) with a literal == -> 0 in-window rows -> verify-fail every region -> no bank, no .ld.bin reclaim -> scratch fill (agent killed it at 82% disk, freed to 42%, 0 banked so nothing lost). FIXED + PUSHED (baeb925 fix+regression via _chrom_match_key strip-chr on both sides, a5a5f9f docs; origin==local==a5a5f9f; tests/m3 28+14 passed; quick 260628-244). Also repaired 10 dangling git index blobs lost from the object store (git hash-object -w). Agent git-pulled a5a5f9f, pre-flight confirmed region-1 chr1 window = 102,421 (== plink log), RE-FIRED clean 05:44:59 UTC. Carter ordered STOP-on-complete (the VM is STOPPED, NOT deleted, at 276 - VM+PD+local bfile preserved, resume-safe; any delete is a separate Carter action). Liveness = bucket .npz count -> 276; do NOT restart kernel. Proof point = region 1 ~06:42 UTC (npz 0->1 + df back to ~42% = reclaim). PRIOR 2026-06-27 ~04:25Z - LOOP RUNNING (SUPERSEDED, this is the fire that banked 0/276): the 276-region AFR native-plink LD loop FIRED + clean-started 04:17:52 UTC on the Hail-free Cloud Analysis VM AoU_Jupyter_ComputeEngine_20260626b (n2-standard-16, 1TB disk, $0.83/hr, autostop disabled), nohup PID 4237, timeout 312h, server-side. Clean start: AFR count 276, region 1 (m2_region_00001 chr1) computing, plink v1.90b7.2 --r square bin4 --keep-allele-order, bfile 73,122x20.7M loaded, df 391G/554G stable, npz_count=0 (region 1 banks ~1h). Liveness = climbing bucket .npz count -> 276 (NOT kernel/log); do NOT restart kernel; resume-safe; timeout 312h ~$259 ceiling; NO self-teardown (pet SA list-only -> UI teardown). 2-3 day cadence. This session: Phase 1 EXPORT DONE+byte-verified (.bed 379,657,321,787 B -> gs://.../ld/afr_native_panel/bfile/; plink staged to gs://.../tools/; cluster 20260604 STOPPED); plan PIVOTED off single-node-Dataproc (IAM-dead, pet SA list-only -> reference_aou_pet_sa_listonly_dataproc) to the decoupled Hail-free fallback; driver scratch-fill bug FIXED @ 783ba91 (_reclaim_region_scratch, 24/24 tests, caught pre-fire); 500GB PD too small (base image eats ~192GiB) -> re-provisioned 1TB (reference_aou_analysis_vm_large_bfile_staging); gsutil -m cp died sparse -> gcloud storage cp + verify by stat/df not ls. Pending: agent confirms npz 0->1 + post-region-2 df/reclaim; Carter UI-deletes stopped cluster 20260604 (~$169 standby). Resume = .planning/HANDOFF.json 04:25Z block. PRIOR 2026-06-26 ~23:35Z (SUPERSEDED) - MID-FIRE: Phase 1 EXPORT running in-perimeter on Hail cluster 20260604 (UI-started, attended at 15-min cadence). export_cohort_to_plink writing the AFR bfile DIRECT to gs://.../ld/afr_native_panel/bfile/afr_cohort (single-driver merge of 353.6G in progress; bucket showing only .fam mid-merge = EXPECTED; liveness=driver Java CPU/network). PLAN PIVOTED off single-node-Dataproc (DEAD: UI can't convert Standard->single-node in-place; the in-perimeter pet SA is list-only Dataproc so no gcloud create + no in-node self-delete - verified via testIamPermissions, memory reference_aou_pet_sa_listonly_dataproc) to the DECOUPLED HAIL-FREE FALLBACK (Carter-authorized, ~$260 total): export->bucket bfile on the UI-started Hail cluster, then the 276-region plink loop on a SEPARATE UI-managed Cloud Analysis VM (n2-standard-16, 500GB reattachable PD, Hail-free; nohup+timeout 312h; NO self-delete - teardown is UI-only). Agent stages plink1.9 to gs://.../tools/ BEFORE stopping + byte-verifies the bfile + UI-stops 20260604, then HOLDS for Carter's Phase 2 go. Liveness Phase 2 = bucket .npz count->276. Resume=.planning/HANDOFF.json 23:35Z block. PRIOR 2026-06-26 ~17:20Z (was-LATEST, NOW SUPERSEDED - the single-node-convert fire was IAM-blocked + never ran) - SESSION CLOSED MID-FIRE (Carter moving). The m3-02e-T4 276-region single-node native-plink LD loop was to be FIRED AUTONOMOUSLY by the in-perimeter AOU agent, server-side. Compute shape DECIDED: single-node n2-standard-16 Dataproc (converted in place from the 25-node $24.07/hr HAIL cluster 20604), serial --num-shards 1, ~11 days, ~$250-300 on-demand, timeout-312h = ~$293 hard ceiling. 8-VM fast path killed (infeasible to provision). Agent sequence: stop->convert(single-node,>=500GB,HAIL,DESTRUCTIVE wipe-mirror-done-first)->start->2 gates($/hr + self-delete dry-test)->git pull 10aaa6f->STEP2 export-once(AFR MT->LOCAL /home/jupyter/afr_cohort; bfile is LOCAL not gs:// - plink can't read gs://)->fire trap-EXIT+timeout-312h wrapped loop(.npz->gs://.../ld/afr_native_panel/)->2-3d check-ins. Disk-safety gate CLEARED: forensic mirror byte-verified (24 objs/14,383,272 bytes) to gs://.../forensics_archive/m3-W2-localdisk-mirror-20260626T171108Z before the wipe. 3-layer backstop (timeout+trap+check-ins) replaces the un-settable --max-age TTL. Resume signal=native-panel-recorded. ON RECONNECT: do NOT restart kernel; FIRST check agent's last report + cluster state + bucket .npz count (climbing->276). PRIOR 2026-06-26 (earlier) - SESSION CLOSED for the night; $0 in-perimeter (cluster 20260604 STOPPED). m3-02e-T4 STEP 3 ACCEPTED (budget gate satisfied). Resumable native-plink loop driver BUILT+verified+8-VM-sharded (quick 260625-r6m; commits 35361e5/1a1a361/cdc2103; full suite 287/0/30; fire brief STEP 4/7 updated). NCSU background job at close: driver GCS-durability fix (gs:// out-dir via gsutil, Hail-free) finishing its ~46-min suite then auto-commit+push -> driver ~1 commit ahead of origin 1b68192 by morning (git pull first). 8-VM/~$50/1.4-day fast path INFEASIBLE unattended (agent can't provision 8 Spot VMs; NCSU wb-CLI no create + gcloud VPC-SC-walled; plink saturates 16 cores so 1 box can't beat ~11d) -> only executable shape = single-node n2-standard-16 Dataproc, serial, ~11 days, ~$250-300 (under Carter's $500 cap). STEP 2 export-once PENDING (full-cohort bfile doesn't exist; only the 1-region pilot bfile). NEXT (Carter, AM): git pull -> pick compute shape -> export-once -> fire loop unattended (gs:// out-dir, self-stop/wall-capped) -> verify+egress+handback -> m3-04 REPLAN. PRIOR 2026-06-25 - m3-02e-T4 STEP 3 production-VM re-measure gate RUNNING in-perimeter (billable; plink PID 6063, square mode, cluster 20260604 master n2-standard-16, ~56min); Carter authorized STEP 0 + STEP 3 ONLY then went home, session disconnecting. Server-side, survives disconnect (do NOT restart kernel; 0-byte .ld.bin is NORMAL for square; liveness=plink %CPU+RES). HARD STOP after STEP 3 -> capture wall/RAM/output -> NCSU projects x276 + 15-20% tail -> budget gate. Open: budget cap PENDING, production-VM type to confirm. NCSU all pushed @ 80fbb9a (m3-02e T1-3 + stitch flake-class debug RESOLVED via shared R_SUBPROCESS_TIMEOUT_S in tests/conftest.py; full-suite 271/30/0). PRIOR 2026-06-19 (latest) - m3-02b EXECUTED (overlapping-window xlarge split + BANDED stitch + A6 real-loader verify + Q-RS2 cell, 3 TDD tasks) then adversarially code-reviewed (CR-01 full-matrix LD doubling + WR-01/02/03, all fixed TDD) then blast-radius swept (4 parallel agents) which CAUGHT BR-01 — the CR-01 fix made the lower_triangular flag authoritative but bm_to_npz.py (Path A.3) never wrote it -> A.3 off-diagonals HALVED; FIXED with 2 RED-first tests; a stale liftover test was also exposed+corrected (UCSC chain truth 53843159). A.3 AF sidecar gap (bm_to_npz writes no allele_freq) DEFERRED+tracked as a m3-04 precondition. Full tests/m3 194 passed/0 failed/30 skipped. NOTHING running (code-only session). NEXT = m3-02c (quota + real-cohort cost probe + go/no-go; autonomous:false; Carter fires in-perimeter, costs money). PRIOR 2026-06-18 - dev-10 LD fire KILLED as intractable on the dev cluster (real-cohort 73k-220k samples make each block ~36-110x heavier than the --n-samples=2000 repro measured; region_00006 crawled ~1-2 blocks/min + master crashed at ~65 GiB dense scratch; 0 regions completed). A.3 fix correctness NOT in question; cluster STOPPED, orphan scratch deleted. NEXT = Wave-2 RE-SCOPE via /gsd-plan-phase (sized cluster + xlarge region-splitting + cost-model redo) per WAVE-2-RESCOPE-real-cohort-compute.md. PRIOR 2026-06-18 (later) - GATE-2 dev-10 LD fire FIRED + RUNNING server-side (Cell 6 loop, AOU-2, USE_DEV_SUBSET=True, cluster 20260617, Spark app application_1781785150907_0001, ordering A, A.3 fix cluster-validated); region_00006 computing first (the hang-proof region); Carter stepped away — resume via .planning/HANDOFF.json (do NOT restart kernel; liveness = data layer). PRIOR 2026-06-18 - Completed quick task 260618-3at: A.3 ordering experiment ran on a 16-worker cluster resize → ordering A COMPLETED 928s (first cluster validation of the deployed fix), ordering B COMPLETED 863s (hang-free) but `banded==dense` for all 23 A.3 regions → KEEP ordering A, RETIRE ordering B; CR-01 reframed as ordering-independent (real GATE-3 question = xlarge dense-materialize cost vs region-splitting); debug session RESOLVED; cluster being Stopped. PRIOR 2026-06-12 - GATE-2 dev-10 FIRED (after GATE-1 cost cleared) then PAUSED: region 1 (m2_region_00006, n_var=122,678) HUNG on the first live Path-A.3 BlockMatrix write (hl.ld_matrix().write() → interpreted BlockMatrixWrite via driver-side ContextRDD.collect, 736/900 in ~73min; killed via Spark-UI job-kill; 99 GB orphan .bm deleted+verified; cluster STOPPED by Carter, $0; Hail session cold). FIX landed + DOUBLE-REVIEWED (gsd + adversarial-vs-Hail-source) — Path A.3 now `_write_a3_banded_correlation_bm` (row_correlation → checkpoint → locus_windows → sparsify_row_intervals(blocks_only=False) → write), byte-identical to ld_matrix; tests/m3 155 passed; commits 125b353 fix / 13a1055 + a554c26 remediation / 4fb40bd + 69c1bfa docs. Adversarial pass corrected the mechanism (warning fires on ALL BlockMatrix writes per CanLowerEfficiently.scala — fix is cheap because final write reads CONCRETE blocks) + surfaced CR-01 (ordering A checkpoints FULL DENSE n×n → ~2 TB scratch on largest region = GATE-3 blocker) + that Pan-UKBB uses ordering B (band-then-checkpoint, ~GB) at scale → B is the leading production default. NEXT: restart cluster (wb cluster start ...20260605) → git pull a554c26 → run scripts/a3_blockmatrix_lowering_repro.py (re-gated on WALL-CLOCK COMPLETION, not the warning; OLD must time out) to pick ordering A vs B by completion+scratch → if B wins, re-order helper band-before-checkpoint → re-fire dev-10 region_00006 data-layer-verified → resume dev-10 → AOU-4 memo. Debug session m3-W2-a3-blockmatrix-write-ir-lowering-hang OPEN at human-verify. PRIOR 2026-06-12 - Completed quick task 260611-tbw: fixed the latent AOU-2 WORKSPACE_BUCKET double-prefix bug (runbook gap C3) — cells 3/4/6 now normalize via the existing `_normalize_bucket` helper (`WB = _normalize_bucket(os.environ["WORKSPACE_BUCKET"])` then `f"gs://{WB}/ld/…"`), matching the panel CLI; surgical nbformat-preserving 7-line notebook diff + a 6th `_normalize_bucket` regression guard (pytest -k normalize_bucket → 6 passed); commits 7e29cd4 (notebook) + c1c7735 (test); notebook NOT executed (VPC-SC). Carter discovered the bug staging the dev-10 fire. ALSO this session: Verily Workbench `wb` CLI installed+authed on the NCSU HPC node (memory reference_wb_cli_hpc_setup) — control-plane works off-perimeter (workspace/resource/cluster), data-plane is VPC-SC-WALLED (gcloud storage → 403 org-policy by request origin), so MT verification + job-submit stay in the Workbench notebook; Hail cluster `…20260605` STARTED via `wb cluster start` and RUNNING (billing). NEXT (Carter, browser): GATE 1 cost okay → `git pull` + `git checkout -f` (your Workbench notebook is the stale pre-ac598ce version) → confirm WORKSPACE_BUCKET → `USE_DEV_SUBSET=True` → run AOU-2 → verify data-layer (Q10/D-M3-07) → AOU-4 memo. PRIOR 2026-06-11 - Completed quick task 260611-f5f: durable-fix atomic-final-write PHASE 2 item 1 — wired the contents-only read_final_cohort_mt gate into AOU-2 cell 4 (the only direct final-MT reader), closing the read-side hole Phase 1 left open; gate-then-read raises a loud RuntimeError (uri + force_fresh=False recovery) before import hail; TDD RED→GREEN, full tests/m3 147 passed/35 skipped (+2); single atomic commit ac598ce; verifier 5/5; chr22 smoke (item 2) + file:// footgun (item 3) stay cluster-deferred behind GATE 1 cost (Carter's trigger). PRIOR 2026-06-06 - Completed quick task 260606-qc1: baked the 3 manual AoU env guards (requester-pays CUSTOM in Cell 1a + HARD-override WORKSPACE_BUCKET/WGS pins in new Cell 1a'') + a RUN PROTOCOL banner (cohorts one-at-a-time, smallest→largest AFR→AFR-sens→EUR, confirm after each, never Run All) into AOU-1_template.ipynb; commit 29d0a1f; 12→14 cells; resolves the long-PENDING durable bake-in from feedback_aou_cluster_template_bucket_pollution; pairs with the genome-wide per-chromosome fan-out wedge fix (ab0853a / debug m3-W2-genome-wide-countcols-py4j-wedge); $0 NCSU-side, Carter holds the cluster/$ trigger. PRIOR 2026-06-02 - Completed quick task 260601-u1b: tiered cheap-first chr22 validation (Tier 0 synthetic probe → Tier 1 nano → Tier 2 chr22) + standalone catastrophe-forensics; 5 commits; plan-check PASSED iter2; verify 8/8 PASSED; code-review SOUND (IN-01 mtime-coerce + IN-02/03 fixed); Track-4 guard byte-identical (md5 16caccec); full tests/m3 109 passed/27 skipped (+15 TDD); repo-only, Carter holds every AoU/$ trigger. 2026-06-02 checkpoint: Gate A cluster path resolved (use the "Hail Genomics Analysis" Dataproc cluster — software-framework=HAIL, Hail pre-installed + YARN-wired; generic "JupyterLab Spark cluster" = no Hail; n2-standard-16 only; web-verified); both prior clusters/envs DELETED = $0; resume = Carter fires Gate A (run sheet in 260601-u1b runbook §0; cluster how-to in memory project_aou_dataproc_hail_install)"
progress:
  total_phases: 12
  completed_phases: 6
```
rc=0

`$ sed -n '1070,1080p' .planning/ROADMAP.md`

```
3. **NaN→0 conditioning util (Python)** — `condition_ld_matrix(m, policy, record)`:
   topology branch (RAISE→drop on fully-NaN rows; zero on isolated pairs), `n_zeroed`
   ceiling (RAISE if exceeded — large NaN fraction is a substrate problem, re-diagnose),
   provenance. Failing-first tests: isolated-pair zeros+records; fully-NaN-row RAISES;
   over-ceiling RAISES.
4. **Conditioned artifact** — write conditioned `.npz`/`.rds` with provenance keys
   (`n_zeroed`, `zeroed_pairs`, `nan_policy`, `psd_method`, `psd_lambda`); leave the raw
   panel `.npz` contract frozen (`ld_npz_to_rds.R` unchanged).
5. **Fit-time wiring + diagnostics** — AFR fit sources `psd_utils.R`; record
   `lambda_method`/`lambda`/`max|R_reg−R|`/min-eigenvalue per region + the credible-set-
   overlap flag & PIP sensitivity for regions containing a zeroed pair.
```
rc=0

`$ for L in 57 113; do printf '%s: ' $L; sed -n "${L}p" .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md | cut -c1-3 | sed 's/^>.*/HISTORICAL (> block)/; s/^[^H].*/LIVE (no > prefix)/'; done`

```
57: HISTORICAL (> block)
113: HISTORICAL (> block)
```
rc=0

### ⚠ F5 ORDERING — the `freeze_state` label vs F5's last drift

`pipeline.schema.yaml` is NOT one of the "7 pinned files" (that list names
four m3-07 modules + three frozen contracts). Its freeze label arrived
separately, via the HANDOFF `freeze_state` field. Is that label BEFORE or
AFTER F5 stopped moving?

`$ git log -1 --format='%h %ad %s' --date=short 63453db`

```
63453db 2026-08-06 docs(handoff): 2026-08-06 close — blast radius REMEDIATED; all gate rows clear but one
```
rc=0

`$ git log -1 --format='%h %ad %s' --date=short 2563451`

```
2563451 2026-08-06 feat(260805-w7u-T1): route the coloc LD path through the resolver; make the manifest fail loudly (FINDING E)
```
rc=0

`$ git merge-base --is-ancestor 2563451 63453db && echo 'ANCESTOR: 2563451 precedes 63453db -- the freeze_state label POSTDATES F5 last drift' || echo 'NOT an ancestor'`

```
ANCESTOR: 2563451 precedes 63453db -- the freeze_state label POSTDATES F5 last drift
```
rc=0

`$ git show '63453db:.planning/HANDOFF.json' | grep -o 'freeze_state[^"]*": "[^"]\{0,320\}'`

```
freeze_state": "run_susie_rss.R RE-FROZEN at dc4bbd2 — the 2026-08-05 unfreeze is SPENT and does NOT carry over; b77 did NOT unfreeze it (its differential test READS it via a body-walk extractor). Six frozen Python modules + src/snakemake/schemas/pipeline.schema.yaml all 0-diff. m3-06 stays HELD (no NaN->0, no condition_ld_matrix.py).
```
rc=0

And the same field TODAY:

`$ grep -n 'freeze_state' .planning/HANDOFF.json | cut -c1-700`

```
124:  "freeze_state": "⚠ RESCOPED 2026-08-06 by quick-260806-sr4 under AUTH-SR4-RESCOPE — THE FREEZE NOW PROTECTS CODE, NOT BYTES. run_susie_rss.R is CODE-frozen at bf04199, declared in exactly ONE place (R_CODE_REF in tests/m3/test_source_freeze_pins.py) and IMPORTED by both consumers, so a re-pinner updates one constant per frozen subject. Comments, docstrings, blank lines and trailing whitespace are now DELIBERATELY FREE; a CODE change still goes RED. Enforced by tests/m3/source_freeze.py (whole-file code-only FLOOR + symbol pins). ALSO NEWLY GATED FOR REAL: plink_ld_to_npz.py, condition_ld_matrix.py, occlusion_span_filter.py (the only three genuinely 0-diff vs bf16289). ⚠ NEVER RE-PIN a 
```
rc=0

### The "7 pinned files" roster, verbatim -- which of the five it names

`$ git show '2bda675:.planning/HANDOFF.json' | grep -o 'All 7 pinned files[^"]\{0,300\}'`

```
All 7 pinned files 0-line diff vs bf16289: the 4 m3-07 modules (occlusion_span_filter, occlusion_manifest, occlusion_present_rate_scan, drop_occluded_from_sumstats) + the 3 frozen contracts (plink_ld_to_npz.py, ld_npz_to_rds.R, condition_ld_matrix.py).
```
rc=0
### ⚠ ORDERING — does the COLLECTIVE label predate the drift it covers?

The earliest readable COLLECTIVE claim is `2bda675` (2026-08-03). F1-F4 are
each NAMED inside its roster. If 2bda675 precedes their drift commits, then a
label -- narrative, unenforced, and phrased as a STATUS REPORT rather than a
prohibition -- did exist before those files moved. That is the single fact
that cuts closest to a FROZEN-AND-DRIFTED reading, so it is measured, not
assumed.

`$ git log -1 --format='%h %ad %s' --date=short 2bda675`

```
2bda675 2026-08-03 docs(handoff): 2026-08-03 close-session — m3-04b landed; AFR_aou panel is UNREACHABLE, do not fire
```
rc=0

`$ git merge-base --is-ancestor 2bda675 3bb8783 && echo '2bda675 PRECEDES 3bb8783 (label predates this drift)' || echo '2bda675 does NOT precede 3bb8783 (drift predates the label)'`

```
2bda675 PRECEDES 3bb8783 (label predates this drift)
```
rc=0

`$ git merge-base --is-ancestor 2bda675 bf963df && echo '2bda675 PRECEDES bf963df (label predates this drift)' || echo '2bda675 does NOT precede bf963df (drift predates the label)'`

```
2bda675 PRECEDES bf963df (label predates this drift)
```
rc=0

`$ git merge-base --is-ancestor 2bda675 fac9a93 && echo '2bda675 PRECEDES fac9a93 (label predates this drift)' || echo '2bda675 does NOT precede fac9a93 (drift predates the label)'`

```
2bda675 PRECEDES fac9a93 (label predates this drift)
```
rc=0

`$ git merge-base --is-ancestor 2bda675 57b381f && echo '2bda675 PRECEDES 57b381f (label predates this drift)' || echo '2bda675 does NOT precede 57b381f (drift predates the label)'`

```
2bda675 PRECEDES 57b381f (label predates this drift)
```
rc=0

`$ git merge-base --is-ancestor 2bda675 d7dfa67 && echo '2bda675 PRECEDES d7dfa67 (label predates this drift)' || echo '2bda675 does NOT precede d7dfa67 (drift predates the label)'`

```
2bda675 does NOT precede d7dfa67 (drift predates the label)
```
rc=0

### The loose line-level criterion produced FALSE POSITIVES. They were READ, not counted.

STEP 5b matched any line carrying BOTH a basename AND a freeze word. Reading
the earliest hits shows most are INCIDENTAL co-occurrence, not freeze claims
about that file. Two worked examples:

`$ git show 'e3075ae:.planning/HANDOFF.json' | grep -o 'tests/m3/test_occlusion_present_rate_scan.py:79-84 pins[^"]\{0,120\}'`

```
tests/m3/test_occlusion_present_rate_scan.py:79-84 pins `scan_present_rate` to return a dict keyed by a (chr, pos) TUPLE on GRCh37 (`target = (1, 5_982_778)`; the string `vari
```
rc=0

-> "pins" here means a TEST pins a RETURN TYPE. It is not a freeze claim.

`$ git show '262ff12:.planning/HANDOFF.json' | grep -o 'ld_npz_to_rds[^"]\{0,60\}' | head -3`

```
ld_npz_to_rds.R payload reconcile; (3) A6 real-loader verify + sparse-par
```
rc=0

-> an m3-02b work description. Not a freeze claim about the file either.

The GENUINE, individually-naming freeze claims are therefore only these two:

`$ git show '2bda675:.planning/HANDOFF.json' | grep -o 'All 7 pinned files[^"]\{0,300\}'`

```
All 7 pinned files 0-line diff vs bf16289: the 4 m3-07 modules (occlusion_span_filter, occlusion_manifest, occlusion_present_rate_scan, drop_occluded_from_sumstats) + the 3 frozen contracts (plink_ld_to_npz.py, ld_npz_to_rds.R, condition_ld_matrix.py).
```
rc=0

`$ git show '63453db:.planning/HANDOFF.json' | grep -o 'Six frozen Python modules[^"]\{0,90\}'`

```
Six frozen Python modules + src/snakemake/schemas/pipeline.schema.yaml all 0-diff. m3-06 stays HELD (no NaN->0, no 
```
rc=0

---

## STEP 7 — the recommendation, derived MECHANICALLY

The rule, applied per file in order. The first branch that fires wins.

1. **ANY commit untraceable, OR the STEP 3 history INCOMPLETE (`rc != 0`)**
   → `DRIFT-NEEDS-REVIEW`.
2. **ELSE** no `DECISIONS.md` declaration for that file (STEP 5a = 0) **AND**
   `bf16289` enforced by zero tests at the time of the drift (STEP 5d + STEP 6)
   **AND** all drift traceable → `NEVER-FROZEN`.
3. **ELSE** a declaration exists → check the DATE ORDER before labelling.
   Pre-declaration drift is **excluded** from the review set; if 100% of the
   drift predates the only declaration the label is
   `NEVER-FROZEN-UNTIL-DECLARED`, **not** `FROZEN-AND-DRIFTED`.

### The inputs, per branch condition

| Condition | Measured | Command | Result |
|---|---|---|---|
| Any untraceable commit? | 8 distinct drift commits; every one resolves a task token to a real artifact dir AND has its short SHA named inside that artifact | STEP 4 | **NO** — 0 untraceable |
| History incomplete? | all five `git log ... bf16289..HEAD -- <path>` returned `rc=0` | STEP 3 | **NO** — 0 truncated walks |
| `DECISIONS.md` declaration? | `grep -c '<basename>' .planning/DECISIONS.md` = **0** for all five; the register's only freeze entry (`DEC-2026-08-06-sr4-freeze-scope`, line 1039) names **only** C1/C2/C3 at `bf16289` and `run_susie_rss.R` at `bf04199` — `grep -c` inside the entry itself is **0** for all five | STEP 5a, D1 | **NONE** for all five |
| `bf16289` enforced at drift time? | `git grep -c 'bf16289' <commit> -- tests/ src/ config/ Snakefile` returned **0 matching files** at every one of the 8 drift commits | STEP 5d | **ZERO enforcement** |

**Branch 1 does not fire** (no untraceable commit, no truncated walk).
**Branch 2 fires for all five.**
**Branch 3 does not fire** — there is no `DECISIONS.md` declaration to date-order
against. ⚠ This is the branch the plan predicted would not execute. It was
applied anyway rather than skipped, and its guard condition was **measured**
(STEP 5a), not assumed. A rule that is only right because its hard branch never
runs is not a rule.

### The derivation, per file

```
F1  src/python/occlusion_manifest.py
      untraceable=0  history_rc=0  decisions=0  enforced_at_drift=0  traceable=2/2
      -> branch 2 -> NEVER-FROZEN

F2  src/python/occlusion_present_rate_scan.py
      untraceable=0  history_rc=0  decisions=0  enforced_at_drift=0  traceable=3/3
      -> branch 2 -> NEVER-FROZEN

F3  src/python/drop_occluded_from_sumstats.py
      untraceable=0  history_rc=0  decisions=0  enforced_at_drift=0  traceable=2/2
      -> branch 2 -> NEVER-FROZEN

F4  src/scripts/ld_npz_to_rds.R
      untraceable=0  history_rc=0  decisions=0  enforced_at_drift=0  traceable=1/1
      -> branch 2 -> NEVER-FROZEN

F5  src/snakemake/schemas/pipeline.schema.yaml
      untraceable=0  history_rc=0  decisions=0  enforced_at_drift=0  traceable=5/5
      -> branch 2 -> NEVER-FROZEN
```

### ⚠ Two nuances the mechanical rule does NOT capture, recorded so the dossier carries them

**(a) For F1–F4 a narrative label DID exist before the drift.** The collective
roster at `2bda675` (2026-08-03) names F1, F2, F3 and F4 individually and
*precedes* every one of their drift commits (measured by
`git merge-base --is-ancestor`). This is the single fact in the whole corpus
that cuts toward a `FROZEN-AND-DRIFTED` reading. It does not change the
mechanical label — the roster is a **status report** (*"All 7 pinned files
0-line diff vs bf16289"*), not a prohibition; it lives in a handoff narrative,
not the register; and it was enforced by nothing. But it is real, it is
pre-drift, and Carter should see it rather than have it averaged away.

**(b) For F5 the label POSTDATES the drift entirely, and F5 was never in the
roster at all.** `pipeline.schema.yaml` is **not** one of the "7 pinned files"
(that roster is 4 m3-07 modules + 3 frozen contracts). Its only individual
freeze label is the HANDOFF `freeze_state` field at `63453db` (2026-08-06),
and `git merge-base --is-ancestor 2563451 63453db` confirms its last drift
**precedes** that label. Had that label been a `DECISIONS.md` declaration,
branch 3 would have fired and returned `NEVER-FROZEN-UNTIL-DECLARED`. It is
narrative, so branch 2 governs — but the shape is worth stating: **F5 was
declared frozen only after it stopped moving, so there is nothing to review.**

### ⚠ The loose-criterion caveat on `first_readable_frozen_narrative`

STEP 5b's scan matched any line carrying **both** a basename **and** a freeze
word (`frozen|freeze|pinned|pin`). That is deliberately loose — it over-matches,
which is the conservative direction for a *"was it EVER declared frozen?"*
question, because it makes a hit **easier** and therefore makes a null result
**stronger**. But loose matching means the hits must be **read**, not counted,
and reading them shows most are incidental co-occurrence:

- `e3075ae`'s hit for F2 is *"...`test_occlusion_present_rate_scan.py:79-84`
  **pins** `scan_present_rate` to return a dict..."* — a TEST pinning a RETURN
  TYPE. Not a freeze claim.
- `262ff12`'s hit for F4 (2026-06-19) is an m3-02b work description. Not a
  freeze claim.

So the raw earliest-hit dates (F4 at 2026-06-19, etc.) are **NOT** freeze-label
dates and must not be reported as such. The **genuine, individually-naming**
freeze claims are exactly two: the `2bda675` roster (F1–F4) and the `63453db`
`freeze_state` field (F5). Those are the values carried into the TSV.

**Every one of these dates remains a LOWER BOUND** — 17 revisions of
`HANDOFF.json`, 29 of `STATE.md` and 22 of `.continue-here.md` were unreadable,
and the unreadable set skews OLD (see OBJECT-STORE CENSUS).
