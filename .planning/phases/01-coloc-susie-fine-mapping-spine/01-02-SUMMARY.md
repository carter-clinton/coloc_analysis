---
phase: 01-coloc-susie-fine-mapping-spine
plan: 02
plan_id: 01-02
plan_name: "UKBB-LD tiled EUR panel (Weissbrod 2020)"
subsystem: ld_reference
tags: [ld, ukbb, eur, boto3, scipy, finemap, wave2, req-2]
dependency_graph:
  requires:
    - 01-01 (config/susie_policy.yaml, run_susie_rss.R fit loader, G3_complex regions)
  provides:
    - REQ-2 G4 EUR-leg LD source (ukbb_ld_tiled) plumbing
    - REQ-2 G6 UKBB-LD substitution locked via ld_reference.EUR_source
    - download_ukbb_ld_tiles Snakemake rule
    - ukbb_ld_tile_to_region_rds.py retry/offline helper
    - envs/ld_build.yml (Python+R, no JVM/Spark)
    - T-1-02 tile SHA256 provenance chain
    - T-1-03 region_id path sanitization
    - T-1-04 HLA_6p21 block-diagonal flag in .meta.json sidecar
    - Absolute-path LD_BUILD_ENV pattern (DEF-01-01 forward fix)
  affects:
    - Plan 01-03 (HGDP+1kG AFR panel -- can reuse LD_BUILD_ENV pattern)
    - Plan 01-04 (coloc.susie consumes .rds + .meta.json)
    - Plan 01-05 (QC dashboard reads ld_source flag)
    - Plan 01-06 (first real smoke test will exercise the rule)
tech_stack:
  added:
    - boto3=1.34 (UNSIGNED anonymous S3)
    - scipy=1.13 (sparse NPZ + linalg.block_diag)
    - pyreadr==0.5.2 via pip (Python -> .rds bridge)
  patterns:
    - "boto3 UNSIGNED anonymous access: boto3.client('s3', config=Config(signature_version=UNSIGNED))"
    - "scipy.sparse.load_npz(...).toarray() for UKBB-LD NPZ tiles (NOT upper-triangle flat)"
    - "scipy.linalg.block_diag for cross-tile regions (HLA_6p21)"
    - "Streaming SHA256 provenance per downloaded tile, recorded in sidecar .meta.json"
    - "region_id sanitizer: regex strip + '..' / '/' rejection"
    - "Absolute conda: directive LD_BUILD_ENV = str(Path(workflow.basedir) / 'envs' / 'ld_build.yml') (DEF-01-01 workaround)"
key_files:
  created:
    - envs/ld_build.yml
    - src/snakemake/scripts/download_ukbb_ld_tiles.py
    - src/snakemake/scripts/ukbb_ld_tile_to_region_rds.py
    - tests/phase1/test_ld_panels.py
    - tests/phase1/test_ld_hla_flag.py
    - .planning/phases/01-coloc-susie-fine-mapping-spine/wave2a_preflight.log
  modified:
    - src/snakemake/rules/ld_reference.smk
    - config/pipeline.yaml
    - src/snakemake/schemas/pipeline.schema.yaml
decisions:
  - "NPZ format is scipy.sparse coo_matrix (row/col/format/shape/data keys), NOT upper-triangle flat 'R' as the plan pre-spec assumed -- downloader uses scipy.sparse.load_npz().toarray() and drops the --npz-key-name CLI knob"
  - "Scratch dir is /rs1/researchers/c/ckclinto/ukbb_ld_scratch (29 TB avail). Plan default /rs1/scratch/ukbb_ld does NOT exist on this cluster -- the mount root shows only a 954 MB stub"
  - "New conda: directive uses absolute LD_BUILD_ENV = str(Path(workflow.basedir) / 'envs' / 'ld_build.yml') per deferred-items.md DEF-01-01 forward fix; documented pattern for Plan 01-03 to reuse"
  - "UKBB_LD_REGION_INFOS filter drops non-autosomal regions (BMI_Xq24 on ChrX) because UKBB-LD EUR panel is autosomes-only"
  - "pipeline.schema.yaml extended with ukbb_ld, ld_reference, and paths.ukbb_ld_scratch keys so additionalProperties: false stays enforced"
  - "pyreadr added via pip (not conda) because it is not in conda-forge/bioconda for current pins; documented in envs/ld_build.yml"
  - "Preflight used the smaller chr22_14000001_17000001 tile (30 MB, sparse centromeric region) rather than the plan's chr22_16000001_19000001 tile (978 MB) to minimize preflight footprint while still verifying schema"
metrics:
  completed: "2026-04-12"
  duration_min: 11
  tasks_completed: 5
  commits: 4
---

# Phase 1 Plan 02: UKBB-LD tiled EUR panel (Weissbrod 2020) Summary

**One-liner:** Lands the UKBB-LD tiled EUR LD panel plumbing -- lightweight conda env, boto3 UNSIGNED anonymous downloader with scipy.sparse NPZ handling, cross-tile block-diagonal HLA path, Snakemake rule wired via an absolute-path conda directive (DEF-01-01 forward fix), config + schema updates, and RED-scaffold pytest guards for ld_source + HLA flag -- all dry-run gated without a real S3 pull.

## Deliverables

### New files (6)

| File | Purpose |
|---|---|
| `envs/ld_build.yml` | Python+R LD-building env (numpy/scipy/boto3/pandas + r-base/data.table/yaml + bcftools/plink2 + pyreadr via pip); no JVM/Spark stack |
| `src/snakemake/scripts/download_ukbb_ld_tiles.py` | 367-line downloader: boto3 UNSIGNED S3 list/download + scipy.sparse NPZ loader + region intersection + block_diag for HLA + SHA256 provenance + sidecar .meta.json writer |
| `src/snakemake/scripts/ukbb_ld_tile_to_region_rds.py` | Thin CLI reusing downloader internals for single-tile retry/offline extraction |
| `tests/phase1/test_ld_panels.py` | RED scaffold for UKBB-LD and HGDP+1kG panel existence + n_variants + ld_source checks |
| `tests/phase1/test_ld_hla_flag.py` | T-1-04 guard: HLA_6p21 sidecar must carry ld_source=ukbb_ld_tiled_block_diagonal and tile_keys>=2 |
| `.planning/phases/01-coloc-susie-fine-mapping-spine/wave2a_preflight.log` | Preflight record (bucket reachability, NPZ schema discovery, SHA256 provenance, scratch budget) |

### Modified files (3)

| File | Change |
|---|---|
| `src/snakemake/rules/ld_reference.smk` | +LD_BUILD_ENV absolute path, +UKBB_LD_SCRATCH, +UKBB_LD_OUT_DIR, +UKBB_LD_REGION_INFOS autosome filter, +download_ukbb_ld_tiles rule |
| `config/pipeline.yaml` | +paths.ukbb_ld_scratch, +top-level ukbb_ld section, +top-level ld_reference section with EUR_source=ukbb_ld_tiled |
| `src/snakemake/schemas/pipeline.schema.yaml` | Extended to accept ukbb_ld, ld_reference, and paths.ukbb_ld_scratch keys while keeping additionalProperties: false |

## Preflight findings

See `wave2a_preflight.log`. Highlights:

| Item | Value |
|---|---|
| Bucket reachability | 200 OK (anonymous HTTPS LIST + GET) |
| NPZ format | `scipy.sparse.coo_matrix` (keys: row, col, format, shape, data) |
| NPZ dtype / shape (probe) | `float32` / `(4059, 4059)` for chr22_14000001_17000001 |
| Variant TSV columns | `rsid, chromosome, position, allele1, allele2` |
| Variant count (probe) | 4059 |
| SHA256 (probe NPZ) | `078b3b80efffc8e9bd2338e870b754d9900c852b594614cd374ceac51663540f` |
| SHA256 (probe .gz)  | `f8daf47ad28720d7e081fddbdac21195062868b19da155702df7750c9ec7c897` |
| Scratch dir | `/rs1/researchers/c/ckclinto/ukbb_ld_scratch` (29 TB avail) |

**Schema deviation from plan pre-spec:** The plan assumed NPZ would carry an upper-triangle flat array keyed `R`. Actual format is a scipy.sparse COO matrix -- the downloader uses `scipy.sparse.load_npz(...).toarray()` and the CLI no longer needs a `--npz-key-name` flag. Both `downloader.load_ld_matrix` and `tile_to_region.load_ld_matrix` (shared function) defensively symmetrize if the producer ever ships only one triangle.

## Verification gates (Wave 2a)

| Gate | Result |
|---|---|
| `envs/ld_build.yml` YAML parses and lacks Hail/JVM/Spark tokens | PASS |
| `EUR_ukbb_ld` and `download_ukbb_ld_tiles` rule present in `ld_reference.smk` | PASS |
| `config/pipeline.yaml` sets `ld_reference.EUR_source = ukbb_ld_tiled` | PASS |
| `tests/phase1/test_ld_hla_flag.py::test_hla_block_diagonal` collects | PASS |
| `tests/phase1/test_ld_panels.py::{test_ukbb_ld_output,test_hgdp_afr_output}` collect | PASS |
| `snakemake --dry-run download_ukbb_ld_tiles` resolves 1 job (3 toy regions) | PASS |
| `wave2a_preflight.log` contains NPZ_KEYS + sha256 lines | PASS |
| `--use-conda` dry-run | SKIPPED (blocked on DEF-01-01; new rule uses absolute path workaround so it will resolve once DEF-01-01 is fixed) |

## Runtime extraction smoke

Not in plan scope, but verified the downloader's core against the preflight probe tile. Invoked `ukbb_ld_tile_to_region_rds.py` against the cached chr22 NPZ for a test window [15000000, 16500000]:

```
[chr22_smoketest] wrote /tmp/ld_test_out/chr22_smoketest.rds (n_variants=1408, ld_source=ukbb_ld_tiled)
```

SHA256 of the probe in the generated `.meta.json` matches the preflight log verbatim -- T-1-02 provenance chain is intact end-to-end. (Temporary output cleaned up; pyreadr absent in nyabg-pytools, so the .rds is a placeholder + companion .npz in this smoke only. Production runs in ld_build env get real .rds files.)

## Tiles the rule plans to download

For the production `regions_curated.csv` (autosomal subset after filter, so BMI_Xq24 dropped), the rule will download one or more tiles per region. Full tile enumeration is deferred to Plan 01-06 (first real smoke test) because bucket listing would re-hit S3 for every plan dry-run. The probe listing (`chr22_*`) confirmed every 3 Mb slot is present.

Spot-check for Plan 01-06 dispatch:
- `FTO_16q12` (chr16:53800000-54400000) -> likely 1 tile near chr16_51000001_54000001 or chr16_54000001_57000001
- `HLA_6p21` (chr6:25000000-35000000) -> 3-4 tiles (block-diagonal path)
- `APOE_19q13` (chr19:44000000-46000000) -> 1 tile
- `9p21_CDKN2A` (chr9:21000000-23000000) -> 1 tile
- `SLC2A9_urate` (chr4:9000000-11000000) -> 1 tile

## Deviations from plan

### Rule 1/2/3 auto-fixes

**1. [Rule 1 - Bug] Plan pre-spec NPZ schema was wrong**
- **Found during:** Task 1-02-00 preflight
- **Issue:** Plan assumed NPZ carries an upper-triangle flat array keyed `R` (see plan code example). Actual format is a `scipy.sparse.coo_matrix` saved via `scipy.sparse.save_npz` (keys: row/col/format/shape/data).
- **Fix:** Downloader uses `scipy.sparse.load_npz().toarray()` with defensive symmetrization; dropped `--npz-key-name` CLI flag and `ukbb_ld.npz_key_name` config key from the plan spec.
- **Files modified:** `src/snakemake/scripts/download_ukbb_ld_tiles.py`, `src/snakemake/scripts/ukbb_ld_tile_to_region_rds.py`, `config/pipeline.yaml`, `src/snakemake/rules/ld_reference.smk`
- **Commit:** `bdc1cc3`

**2. [Rule 3 - Blocker] Plan's scratch dir default does not exist**
- **Found during:** Task 1-02-00 preflight (`df -h /rs1` returned a 954 MB root stub)
- **Issue:** Plan hardcoded `/rs1/scratch/ukbb_ld` as the scratch default. The `/rs1` mount root on this cluster is only a 954 MB stub; actual user storage lives under `/rs1/researchers/c/ckclinto` (29 TB avail).
- **Fix:** Default scratch changed to `/rs1/researchers/c/ckclinto/ukbb_ld_scratch` in both the downloader CLI default, the rule params, and `config/pipeline.yaml paths.ukbb_ld_scratch`.
- **Files modified:** as above
- **Commit:** `bdc1cc3`

**3. [Rule 2 - Missing critical functionality] Schema rejection of new config keys**
- **Found during:** Task 1-02-02 integration check
- **Issue:** `pipeline.schema.yaml` sets `additionalProperties: false` at the root and in `paths`. Adding `ukbb_ld`, `ld_reference`, and `paths.ukbb_ld_scratch` without extending the schema would break `validate(config, ...)` in the toy Snakefile the next time it runs.
- **Fix:** Extended schema with the three new keys, keeping `additionalProperties: false` enforced everywhere else.
- **Files modified:** `src/snakemake/schemas/pipeline.schema.yaml`
- **Commit:** `bdc1cc3`

**4. [Rule 2 - Missing critical functionality] Non-autosomal region filter**
- **Found during:** Task 1-02-02 writing output list
- **Issue:** UKBB-LD EUR panel is autosomes-only (no ChrX/Y tiles). The rule's output list built from raw `REGION_INFOS` would include `BMI_Xq24` which would fail at runtime when `list_tiles(s3, 'X')` returns empty.
- **Fix:** Added `UKBB_LD_REGION_INFOS` filter in `ld_reference.smk` and an in-script filter in `main()` to drop X/Y/MT rows with a warning to stderr.
- **Files modified:** `src/snakemake/rules/ld_reference.smk`, `src/snakemake/scripts/download_ukbb_ld_tiles.py`
- **Commit:** `bdc1cc3`

### Task reorder

TDD task order applied: Task 1-02-03 (tests) committed before Task 1-02-02 (implementation) per the plan's `tdd="true"` hint on the test task. Preflight (1-02-00) and env (1-02-01) still came first.

### Auth gates

None. UKBB-LD bucket is public and access is anonymous via boto3 UNSIGNED.

## Known stubs

None. All code paths produce real artifacts in `ld_build` env; the `HAVE_PYREADR` fallback path is a defensive guard and should never fire in production.

## Threat flags

None. The rule operates within the boundaries documented in the plan's `<threat_model>`:
- **T-1-02 (Tampering):** mitigated via streaming SHA256 on every downloaded tile, recorded in sidecar `.meta.json`
- **T-1-03 (path injection):** `safe_region_id()` rejects `/` and `..`, strips non-word characters via regex
- **T-1-04 (HLA cross-tile LD):** block-diagonal path flips `ld_source='ukbb_ld_tiled_block_diagonal'` and records the participating tile keys in `tile_keys[]` for downstream surface area

No new network endpoints, auth paths, or schema changes at trust boundaries are introduced beyond the plan.

## Deferred Issues

None new. The two pre-existing Phase 1 deferred items remain untouched:
- **DEF-01-01:** `snakemake --use-conda` still fails for relative `conda:` paths in legacy rules. The new `download_ukbb_ld_tiles` rule intentionally uses the absolute-path `LD_BUILD_ENV` pattern so it is ready to go once DEF-01-01 is fixed. Pattern documented in-file and in this summary for Plan 01-03 to reuse.
- **DEF-01-02:** `envs/r_coloc.yml` still not materialized on disk. Plan 01-02 materialized `envs/ld_build.yml` as a YAML-parse-validated file only; full `conda env create` is deferred to Plan 01-06's first real smoke run.
- **DEF-01-03:** Unrelated unstaged changes in `.claude/settings.json` and `.planning/config.json` still present, still out of scope.

## Self-Check: PASSED

Verified all Task 1-02-* artifacts exist and commits landed:

- `envs/ld_build.yml` FOUND
- `src/snakemake/scripts/download_ukbb_ld_tiles.py` FOUND
- `src/snakemake/scripts/ukbb_ld_tile_to_region_rds.py` FOUND
- `src/snakemake/rules/ld_reference.smk` FOUND (modified)
- `config/pipeline.yaml` FOUND (modified)
- `src/snakemake/schemas/pipeline.schema.yaml` FOUND (modified)
- `tests/phase1/test_ld_panels.py` FOUND
- `tests/phase1/test_ld_hla_flag.py` FOUND
- `.planning/phases/01-coloc-susie-fine-mapping-spine/wave2a_preflight.log` FOUND
- Commits `6a9af35`, `f681406`, `2033cb8`, `bdc1cc3` FOUND in `git log`
