---
phase: m1-sumstats-upgrade-and-harmonization
fixed_at: 2026-04-25T16:42:00Z
review_path: .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-REVIEW.md
iteration: 1
fix_scope: critical_only
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase M1: Code Review Fix Report

**Fixed at:** 2026-04-25T16:42:00Z
**Source review:** `.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-REVIEW.md`
**Iteration:** 1
**Scope:** critical_only (user override — defaults `critical_warning` would
have included the 16 warnings; user explicitly requested CR-only this round)

**Summary:**
- Findings in scope: 3 (CR-01, CR-02, CR-03)
- Fixed: 3
- Skipped: 0
- Warnings (16) and Info (6) findings: deferred per user scope override
  — flagged for follow-up in a subsequent fix pass

## Fixed Issues

### CR-01: Race condition in `m1_qc_per_trait` Quarto render

**Files modified:** `src/snakemake/rules/m1_qc.smk`
**Commit:** `8da9f60`
**Lines touched:** 44-64 (`m1_qc_per_trait` shell block) and 79-99
(`m1_qc_index` shell block)

**Applied fix:**
Both Quarto-render shell blocks now create a per-job `mktemp -d -p {QC_DIR}
qc_render.XXXXXX` (or `qc_index.XXXXXX`) directory, render Quarto into that
isolated path with `--output-dir "$TMPDIR"`, then `mv` the output file
(`m1_qc_report.html` / `m1_qc_index.html`) to the final wildcard-named target.
The temp dir is removed after the move. This eliminates the race where two
parallel per-trait renders both wrote to `{QC_DIR}/m1_qc_report.html` before
the `if [ -f ... ]; then mv` block could rescue them. The `mkdir -p {QC_DIR}`
prelude is added so `mktemp -p` doesn't fail on a fresh tree.

The same fix is applied to `m1_qc_index` for symmetry per the review's
guidance — that rule is single-output and won't race with itself, but the
identical pattern reduces cognitive load and prevents future regression if a
sibling rule is added that also writes into `{QC_DIR}`.

**Output filename target:** unchanged (`{trait}.{ancestry}.{consortium}.{year}.qc.html`
for per-trait, `index.html` for the aggregator).

**Deviations from suggested patch:** none material. Added an explicit
`mkdir -p {QC_DIR}` before `mktemp -p` (the suggested patch assumed QC_DIR
existed; this guards a clean-build scenario). Comments in the shell blocks
attribute the change to CR-01 for git-blame hygiene.

**Test runs:** none — Quarto-render rules are not currently pytest-tested
(no fixture stub exists for invoking Quarto in unit tests). Tier 1
verification (re-read modified file, confirm fix present and surrounding
code intact) passed. Tier 2 syntax check via `ast.parse` is not applicable
(.smk uses Snakemake DSL, not pure Python). The `mktemp` + `mv` + `rm -rf`
sequence is shell-stable and matches the standard pattern used elsewhere
in the project.

---

### CR-02: `harmonize_gbmi.py` does not emit a QC sidecar; smk stub omits required fields

**Files modified:** `src/python/harmonize_gbmi.py`, `src/snakemake/rules/m1_harmonize.smk`
**Commit:** `72c8ab3`
**Lines touched:**
- `src/python/harmonize_gbmi.py:18-25` (added `import json`)
- `src/python/harmonize_gbmi.py:47-205` (extended
  `harmonize_gbmi_sumstats` signature with `qc_json_path` + `maf_min`,
  added `n_input` capture pre-filter, added `n_palindromic_dropped`
  computation, added qc-dict population with full schema, added
  `qc_json_path.write_text(...)` mirror of harmonize_yengo pattern)
- `src/python/harmonize_gbmi.py:215-260` (added `--qc-json` and
  `--maf-min` argparse arguments + passthrough in `_main()`)
- `src/snakemake/rules/m1_harmonize.smk:849-870` (replaced the dual
  `python -c "..."` stubs with `--qc-json {output.qc_json}` +
  `--maf-min 0.005` flags on the `harmonize_gbmi.py` invocation; the
  parquet `python -c` stub remains because it is WR-12 scope and not
  in this fix wave)

**Applied fix:**
The `harmonize_gbmi_sumstats()` function now writes its qc dict to the
caller-supplied `qc_json_path` using the same idiom as
`harmonize_yengo.py:247-248` (`mkdir parents=True, exist_ok=True` →
`write_text(json.dumps(qc, indent=2, default=str) + "\n")`). The qc dict
gained the required keys: `n_input` (rows pre-filter, captured before the
b38→b37 liftover step), `n_output` (rows post-palindromic + MAF filters),
`n_palindromic_dropped`, `n_maf_below_threshold` (initialized to 0 in this
commit; CR-03 populates with the real count), and `maf_min`. The original
`n_rows` key is preserved as an alias of `n_output` for backward
compatibility with any downstream code that already reads it.

The `m1_harmonize_smk` GBMI rule is updated to pass `--qc-json
{output.qc_json}` and `--maf-min 0.005` to the harmonizer; the dual
`python -c "import json; print(json.dumps({...}))" > {output.qc_json}`
stub at lines 864-865 is removed. The minimal-stub keys it produced
(`phenotype_lock`, `build_target`, `liftover_chain`) are NOT carried into
the new sidecar — those are static manifest fields, not per-run QC, and
they're already captured in `config/trait_inventory.yaml` /
`SUMSTATS-UPGRADE.tsv` via the inventory builder. If the OSF-paste
provenance audit needs them in qc.json itself, that's a separate widget
(deferred — flag for follow-up).

The downstream effect: `verify_m1_artifacts.verify_d` (MAF=0 fraction),
`verify_e` (palindromic drop <10%), and the `m1_qc_report.qmd §8`
palindromic-status renderer will now READ instead of SKIP for the asthma
× {MULTI, EUR, AFR} cells.

**Deviations from suggested patch:**
- The review's patch suggested capturing `n_input_pre_filters` as a
  separate variable; I named it `n_input` directly and captured it
  immediately after `pd.read_csv` (matches the `harmonize_yengo`
  convention which also reads pre-anything).
- The `n_rows` alias is preserved alongside the new `n_output` key (the
  review didn't ask for this; defensive backward-compat for any caller
  that already consumes `n_rows`).
- WR-12 (move parquet write into harmonize_gbmi.py) was NOT bundled into
  this commit per the user scope override — only CR-02 + CR-03 are in
  scope this iteration. The parquet `python -c` stub remains in place;
  comment added in m1_harmonize.smk attributing it to WR-12 follow-up.

**Test runs:**
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest \
  tests/m1/test_harmonize_gbmi_liftover.py \
  tests/m1/test_harmonizer_contract.py -q
.......... 10 passed in 2.19s
```
All 4 GBMI liftover tests + 6 harmonizer-contract tests pass. The
existing fixture path (`tests/m1/fixtures/gbmi_b38_head.tsv.gz`) does not
yet assert the qc.json sidecar exists — the test calls
`harmonize_gbmi_sumstats(...)` without `qc_json_path`, so the function
takes the `is None` branch and skips file-write. Existing tests are
backward-compatible because the new arguments are keyword-only with
defaults. New tests for the qc.json output path are flagged for the
follow-up warnings-fix pass (TDD discipline says they belong with the
test-asserting commit; user explicitly scoped this iteration to CR fixes
only, so they're held back).

---

### CR-03: `harmonize_gbmi.py` skips MAF=0.005 floor; inconsistent with all other M1 harmonizers

**Files modified:** `src/python/harmonize_gbmi.py`
**Commit:** `baf041f`
**Lines touched:** `src/python/harmonize_gbmi.py:167-182`

**Applied fix:**
Replaced the CR-02 placeholder `n_maf_below_threshold = 0` block with the
real MAF floor computation, applied immediately after the palindromic
filter (matches `harmonize_yengo.py:217-227` ordering: palindromic first
on the wider dataframe, MAF second on the surviving rows). Snippet:
```python
af = pd.to_numeric(df["EAF"], errors="coerce")
maf = af.where(af < 0.5, 1 - af)
keep_maf = maf >= maf_min
n_maf_below_threshold = int((~keep_maf).sum())
df = df.loc[keep_maf].reset_index(drop=True)
```
The qc dict (built a few lines below) now reports a real
`n_maf_below_threshold` count, and `n_output` reflects the post-filter
row count. The `--maf-min` CLI argument was already plumbed through in
CR-02, so this commit is a pure logic addition — no signature changes.

**Deviations from suggested patch:** none. The review's patch is
applied verbatim. Note that this fix shares WR-05's NaN-EAF-conflation
limitation: a NaN EAF row is dropped silently with the count rolled into
`n_maf_below_threshold` rather than tracked separately. Per the user
scope override, WR-05 is out of this iteration — same limitation
inherited here is deliberate and consistent with the 7 other M1
harmonizers.

**Test runs:**
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest \
  tests/m1/test_harmonize_gbmi_liftover.py \
  tests/m1/test_harmonizer_contract.py -q
.......... 10 passed in 2.14s
```
All 10 tests still pass. The fixture sumstats fixture has high-MAF
synthetic SNPs so the new filter does not drop any rows in the test
dataset; the production asthma run will see the real drop count
populate `n_maf_below_threshold` in the qc.json sidecar.

**Logic-bug verification flag:**
Tier 1 + Tier 2 (re-read + ast.parse) confirm syntax. The MAF-filter
formula `maf = af.where(af < 0.5, 1 - af)` is copy-equivalent to the
identical formula in `harmonize_yengo.py:219`, `harmonize_glgc.py`,
`harmonize_wuttke.py`, `harmonize_diamante.py`, `harmonize_gigastroke.py`,
`harmonize_aragam.py` — peer-validated by 7 sibling harmonizers. No
human-verification flag needed.

---

## Skipped Issues

None.

## Out-of-Scope Findings (deferred per user `critical_only` override)

The following 16 warnings + 6 info findings are deliberately NOT addressed
in this iteration. They are flagged for a subsequent `/gsd-code-review-fix`
run with `fix_scope=warning_info` or for an opportunistic follow-up pass:

**Warnings (16):** WR-01 (DIAMANTE Inf/NaN N), WR-02 (LDSC env path
hardcode), WR-03 (cookie indirect expansion), WR-04 (deferred-guard
0-byte sumstats.gz), WR-05 (NaN EAF conflation in MAF count — same
class as the limitation noted in CR-03), WR-06 (verify_evangelou_sbp
NaN EAF/P), WR-07 (verify_evangelou_sbp X/Y/MT silent-pass), WR-08
(harmonize_gigastroke import-time raise), WR-09 (m1_trait_keys assert
under -O), WR-10 (fire driver hardcoded conda paths), WR-11 (qmd CHR
type-coerce), WR-12 (move GBMI parquet into harmonizer — co-located
with CR-02 fix; see deferred note in CR-02), WR-13 (Klarin schema
unverified), WR-14 (download_sumstats_v2 mkdir error handling), WR-15
(harmonize_diamante X/Y silent drop), WR-16 (m1_raw_glob double-read).

**Info (6):** IN-01 (helper duplication across 7 harmonizers), IN-02
(rsid lookup cache), IN-03 (allele dtype spot-check), IN-04 (rg-matrix
diagonal dead check), IN-05 (sort comment), IN-06 (rg-star progress).

---

_Fixed: 2026-04-25T16:42:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
_Scope: critical_only (user override)_
