---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8a
slug: W3f-collector-drop-audit
type: execute
wave: 15.8a
depends_on: ["ta-r4-W3f-15-7-review-suite-and-close"]
gap_closure: true
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7j-open-items-reply-2026-11-24.txt   # committed as received (bytes unchanged)
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158DIG-reply-2026-11-25.txt     # committed as received
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158R6S-reply-2026-11-25.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158E7R-reply-2026-11-25.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-F3NL-reply-2026-11-25.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158R7-reply-2026-11-25.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-PLAN.md            # the 15.8 planning set (a, b, c, c2, d, e, f), committed here
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-json-full-precision-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-legacy-rule-and-e7-rounding-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-e7-filtered-cs-counts-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-multikey-fatal-and-chronology-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-PLAN.md
  - .planning/DECISIONS.md
  - src/python/ta_r4/collector_drop_audit.py
  - tests/ta_r4/test_collector_drop_audit.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalog_collector_drops.tsv
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates: Carter's Q-157J reply (sha256 805afcd8…503e, free text exactly as in <question>) and the five 2026-11-25 replies (Q-158DIG, Q-158R6S, Q-158E7R, Q-F3NL, Q-158R7; sha256 and label per the <question> table) each pass gate_reply.py through a byte-identical staging copy; otherwise nothing is edited"
    - "The audit replays collect_region_variants.py on the pinned r4 inputs and its kept rows equal the unmodified collector's output for every r4 region (DataFrame-equal, and the written TSV byte-equal to the on-disk variants_r4_raw/<region>.tsv); a region where they differ is a STOP"
    - "Every input row in a region's window that the collector does not keep appears exactly once in that region's audit file with one class (exact_duplicate, rsid_same_key_other_bytes, rsid_other_allele_key, rsid_replaced_allele_less, unnamed_duplicate, unnamed_at_named_position, unnamed_same_position_other_alleles, allele_less) and the flags key_in_final_catalog / swapped_key_in_final_catalog; class `other` or n_input != n_kept + n_dropped is a STOP"
    - "manifests/catalog_collector_drops.tsv gives per region: n_input_rows, n_kept, n_dropped per class, n_lost_keys (dropped rows with real alleles whose normalized CHR:POS:REF:ALT is absent from the final r4 catalog), n_lost_keys_swapped_present, and the audit file's path, rows and sha256"
    - "If n_lost_keys > 0 in any region, the plan stops at Task 2 (checkpoint:human-action, stops even under --auto) with the per-region table; no catalog, panel or pin is changed, and nothing is written to the DRAFT until Carter's reply file exists"
    - "If n_lost_keys == 0 everywhere, the DRAFT (c) clause on the collection step states that its omitted rows are also retained in an audit file and that every omitted row's allele key is in the catalog (counts from the manifest); old string asserted unique"
    - "catalogs_sha256.tsv, catalogs_r4_unique_key.tsv and every catalog/panel byte are unchanged (sha256 before == after)"
  artifacts:
    - path: "src/python/ta_r4/collector_drop_audit.py"
      provides: "replay + classification of the legacy collector's drops"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalog_collector_drops.tsv"
      provides: "per-region drop counts, lost-key counts, audit-file sha256"
  key_links:
    - from: "collector_drop_audit.replay"
      to: "collect_region_variants.collect_variants (unmodified)"
      via: "identity assertion per region"
      pattern: "collect_variants"
---

<objective>
Close review R2 as Carter chose ("R2: measured and audited"). The DRAFT says every row removed from a catalog is in an
audit file, but the collector that runs before catalog_unique_key.py drops rows without one
(collect_region_variants.py:104-116, :143-150, :151-155). This plan audits and counts every such drop on the pinned r4
inputs. If any drop removed an allele key that is absent from the final catalog (fixing it would change a pinned
catalog), it stops for Carter instead of re-pinning. This plan also commits Carter's reply and the 15.8 planning set.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J: file `W3f-carter-15-7j-open-items-reply-2026-11-24.txt`, sha256
`805afcd812902605dd9797d63c15fb201eae1fd2870db348182c1d38a640503e`, 2 lines, LF.
Question text (line 1 after `Question Q-157J (2026-11-24): `): `15.7j brief-blind re-review OPEN items R2 (collector drops unaudited), R3 (E7 count definitions), R4 (QTL posteriors rounded to 4 decimals before thresholds), R5 (multi-key member refusal not fatal), R6 (BLAS library not pinned/checked), R7 (chronology wording). How should each be handled?`
Free text (line 2 after `Carter reply (verbatim): `; note the two spaces in "pin  libopenblas" and the spelling
"recomendations", both verbatim): `continue with your recomendations for the open items R4, R6: pin  libopenblas, R2: measured and audited, R3: yes it should be counted, R5 and R7: go with recommendation`

Task 2 question (only if n_lost_keys > 0), QID Q-158R2, saved by the orchestrator as
`W3f-carter-15-8-Q-158R2-reply-<date>.txt`: "The collector before the allele-key step dropped N input rows whose
allele key is not in the final r4 catalog (per-region table; M of them have the swapped key in the catalog). Restoring
them changes pinned catalogs (and possibly panels). How should 15.8a proceed?" Labels: `A: Keep the catalogs; disclose
the counts in (c) (Recommended)` / `B: Fix the collector step for r4 and rebuild + re-pin the affected catalogs and
panels (new plan; note: a collector fix that keeps same-rsid rows with other allele keys creates multi-key names, which
15.8e makes fatal, so 15.8e's multi-key measurement must be re-run after that rebuild)` / `C: Other (free text)`.
Plan-checker measurement (2026-11-25, current catalogs): 0 rsids with more than one allele key across the 31 r4
catalogs. The recommendation is A only if no lost key is present in any production
panel; Task 1 measures that and the printed label follows the measurement.

**Carter's 2026-11-25 answers** (file `W3f-carter-15-8-<QID>-reply-2026-11-25.txt`, 2 lines, LF; gated by the
staging copy of the protocol with `--question` = line 1 after `Question <QID> (2026-11-25): ` exactly as quoted below
and the label). Question texts (verbatim, one per line):
- Q-158DIG: `Q-158DIG (R4): I recommended 'full precision (digits = NA)'. That was wrong too: in jsonlite, digits = NA means 15 significant digits, not full precision. 0.79999999999999993 is written as 0.8, and only 8.1% of random doubles round-trip; I(17) round-trips 100%. The r4 GWAS pair JSON and the simulation posterior table have the same 15-digit limit, and both feed thresholds. Which fix?`
- Q-158R6S: `R6 reaches Track B: envs/r_coloc.yml is shared with Track B and m3. Pinning libopenblas there changes their env hash, so their next run rebuilds the env from the r4 pin file. The jobs already load 0.3.34, so the version shouldn't change. Also, the guard checks the BLAS pin in every gated r4 job env; python_stats, plink and qtl_processing are unpinned but currently 0.3.34, so the guard fails closed if any of them drifts. Proceed?`
- Q-158E7R: `E7 QTL tiers will mix in rounding: under R4, QTL_A3 posteriors become exact, while QTL_legacy keeps 4-decimal posteriors, matching the earlier pipeline. So E7's qtl_tier 'changed' partly reflects rounding, the same kind of problem as R3. The plan only discloses this. What do you want?`
- Q-F3NL: `Q-F3N again: my earlier question was wrong. I told you E7's frozen comparator QTL_legacy 'does not get the flag'. In the code it does: tiers_argv always passes --nan-gwas-below-threshold, and r4_qtl_tiers runs for every R4 QTL arm, QTL_legacy included. So QTL_legacy's tiers also treat a NaN GWAS PP.H4 as below_threshold. What should QTL_legacy do?`
- Q-158R7: `R7 (15.8e): the planner wrote the Purpose wording you approved under 'go with recommendation', and it will go into public text. It removes '(the pre-lock pilot fits are listed in (h))' and adds the sentence shown in the preview after the 'before any production-arm fit exists' sentence. Approve it?`

| QID | sha256 | label (verbatim) | used by |
|---|---|---|---|
| Q-158DIG | `ea8fe4cdaf4bbcf802d65e68c75e66d3b095777f0e518e9ed57c088d3246ceb4` | `A: Exact round-trip everywhere r4 thresholds (Recommended)` | 15.8c |
| Q-158R6S | `7b3d1045f770bdea49123a85d58866501a46dbe62b0d9ddf5f9ac6bf36875b2d` | `Proceed, pin r_coloc only (Recommended)` | 15.8b |
| Q-158E7R | `43a4d89900c7225576a9edef1980716db999ca8c3193694305fca2c42376bd09` | `Add a matched-rounding column (Recommended)` | 15.8c2 |
| Q-F3NL | `9b4c0bb009e5262c38262da953e2a009b8c1859447bbb0975a24c68c9162b6a1` | `Keep legacy rule for QTL_legacy (Recommended)` | 15.8c2 |
| Q-158R7 | `a9a6866eb9c4b518c7a98206273ddd55fe0cbd4e2e49c1b3d7264d2f69a261b8` | `Approve as written (Recommended)` | 15.8e |
</question>

<protocol>
**15.8 shared protocol** (binding on 15.8a–15.8f; the orchestrator adds it to PLAN-INDEX after 15.7j commits).
- Order 15.8a → 15.8b → 15.8c → 15.8c2 → 15.8d → 15.8e → 15.8f, strictly sequential (all edit the DRAFT, LOG, STATE, PLAN-INDEX).
- `PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11`, `P=.planning/phases/ta-r4-head-to-head-reanalysis-and-submission`,
  `Q8=data/r4/tmp/w3f/q158` (15.8a creates it), `MAN=$P/manifests`.
- **Reply gate.** The 15.7 tool `data/r4/tmp/w3f/q157/gate_reply.py` (unchanged) finds `W3f-carter-15-7-<QID>-reply-<date>.txt`.
  Carter's file has a different name, so every gate copies it byte-for-byte to
  `$Q8/gate/<QID>/W3f-carter-15-7-<QID>-reply-<date>.txt`, `cmp`s the copy with the original, then runs the tool with
  `--dir $Q8/gate/<QID>`. 15.8a writes this as `$Q8/gate_157j.sh` (copy + cmp + tool, `--free-text` as in <question>)
  and negative-controls it: a one-byte change to the copy, and a free text with one space instead of two, each exit 2.
  15.8a also writes `$Q8/gate_158.sh <QID>…`, which gates each named 2026-11-25 reply the same way (staging copy as
  `$Q8/gate/<QID>/W3f-carter-15-7-<QID>-reply-2026-11-25.txt`, `cmp`, then the tool with the question text, sha256 and
  label of the <question> table typed into the script) and negative-controls it once (one byte changed in a copy →
  exit 2). Every 15.8 plan runs `bash $Q8/gate_157j.sh` and `bash $Q8/gate_158.sh` with its own QIDs first, and also
  checks `sha256sum` of each original. Replies to a STOP question (Q-158R2/R3/R5/R6) use the same naming and staging.
  A failed gate is STOP before any edit.
- **Close.** `$Q8/close.sh <tag>` = a copy of `data/r4/tmp/w3f/q157/close.sh` with the junit path changed to
  `$Q8/full_<tag>.xml` (diff shows that line and the `--durations=25` line below). It runs under `sbatch -p compute -A clintonlab_cpu -q normal -t 04:00:00
  --mem=48G --constraint=cascadelake` (non-Cascade-Lake nodes fail the job guard tests). Each plan reconciles per id with
  `$Q8/check_<tag>.py` built on `data/r4/tmp/w3f/q157/check_tmpl.run` (removed ids == declared renames; added ids ==
  `<new_tests>`; outcome changes only on declared spec updates, each passed; 0 failed; totals == base + N_new). close.sh
  passes `--durations=25` to the FULL pytest call (a second diff line), so per-test times are recorded. The id-level
  comparison of two junit files (e.g. full_15_7j vs full_15_7i) uses `data/r4/tmp/w3f/q157/check_tmpl.load` (a
  `load(a) == load(b)` assertion), or `data/r4/tmp/w3f/ukbbi/junit_cmp.py <a> <b>`; there is no junit_cmp copy in
  q157 or q158.
  Base chain: `data/r4/tmp/w3f/q157/full_15_7j.xml` (written by 15.7j; expected 2,694 = 2,641 P / 53 S / 0 F; **use its
  actual totals**, read from the file, never typed; it is identical by id to full_15_7i.xml, and 15.8a asserts that) →
  `$Q8/full_15_8a.xml` → 15_8b → 15_8c → 15_8c2 → 15_8d → `$Q8/full_15_8e.xml`; 15.8f reconciles
  cumulatively against full_15_7j.xml. Restore `tests/m3/sparse_parent_benchmark.tsv` after each FULL.
- **Tests.** RED first: each new test is run and seen to fail (or error on import) before the code exists; each plan
  records at least one negative control per new behaviour (a mutation of the new code that makes its test fail, then
  md5-restored) in `$Q8/nc_<tag>.txt`. Pre-existing tests may be edited only in fixture builders or where a test
  asserts the exact behaviour the plan changes (named by id below, with the reason); ids and passed outcomes stay. Every
  15.8 SUMMARY has a `## Declared spec updates` section (ids one per line, or `none`) and a `## New test ids` section;
  both list ids in junit form, `tests.ta_r4.test_x::test_y`, one per line; 15.8f parses both. Each new test is exactly
  one junit id: no `parametrize` in new tests (otherwise N_new counts junit ids, and the plan says so).
- **DRAFT.** Only the sentence(s) describing the changed behaviour; old string asserted unique; one script per plan;
  `tests/ta_r4/test_amendment_text.py` and `tests/ta_r4/test_prelock_pilot_fits.py` green after. A framing or length
  failure is STOP (the text is not reworded to pass).
- **Never:** `git push`; a production fit; OSF posting; the W4a-T3 lock; `decision_rules.yaml` `locked` changed
  (stays false) or `n_regions_min` changed (stays 7); a re-pin to make a check pass; `git add .` / `-A` (explicit paths).
- `git fsck --connectivity-only` before each commit (memory reference_gpfs_git_object_store_loss).
</protocol>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md
@data/r4/tmp/w3f/q157/disposition_15_7j.md
@src/legacy/region_analysis/scripts/collect_region_variants.py
@src/python/ta_r4/catalog_unique_key.py
@src/snakemake/rules/ta_r4_panels.smk

**Premise, verified at 99ab219d (planning).** collect_region_variants.py drops rows at five points, not the two the
review names:
- :104-110, :111-123 keyed records: a named row is keyed `SNP::<rsid>`, so a second row with the same rsid is not
  stored whatever its alleles; it replaces the stored one only if the stored one lacks real alleles. An unnamed row is
  keyed `POS::chr::pos::ref::alt` (lower-cased) and an exact repeat is skipped (:108-109).
- :142 `drop_duplicates` on the five columns (a no-op after keying, measured by the replay).
- :143-150 an unnamed row at a CHR:POS that carries any named row is removed, whatever the alleles.
- :151-155 `primary_key` = SNP_ID, else CHR:POS: a second unnamed row at the same position with other alleles is
  removed (not named by the review).
The input is the union over the 8 r4 sumstats (`CATALOG_SUMSTATS["r4"]`, ta_r4_panels.smk:14-17, run by
r4_catalog_raw :90-112), so most drops are expected to be the same variant seen in several trait files.
The normalized allele key is catalog_unique_key.py's: `(_norm_chr(CHR), int(POS), REF.strip().upper(), ALT.strip().upper())`
(:70); "swapped" = (chr, pos, ALT, REF).

**Paths.** Raw catalogs `paths.catalog_raw_path(region)` (`data/r4/ld/variants_r4_raw/`), final catalogs
`paths.catalog_path("r4", region)`; r4 regions = the `route == r4` rows of `$MAN/catalogs_sha256.tsv` (31 at
planning). Audit files: `data/r4/ld/variants_r4_collector_dropped/<region>.tsv.gz` (on /rs1 through the data/r4
symlink; durable, sha256 in the manifest).
</context>

<new_tests>
tests/ta_r4/test_collector_drop_audit.py; N_new = 7.
1. `test_replay_keeps_exactly_what_the_collector_keeps` (synthetic multi-file input exercising every drop point;
   replay kept == `collect_variants` output; kept + dropped == input rows)
2. `test_same_rsid_other_allele_key_is_audited`
3. `test_allele_less_record_replaced_by_real_alleles_is_audited`
4. `test_unnamed_at_named_position_is_audited_with_key_flags` (one with the same key as the named row, one with a
   different key: `key_in_final_catalog` true / false; a third whose input differs from the final-catalog row only by
   allele case and a `chr` prefix must be `key_in_final_catalog` true under the normalized key; a fourth whose alleles
   are the swap of a catalog row must be `key_in_final_catalog` false and `swapped_key_in_final_catalog` true)
5. `test_unnamed_same_position_other_alleles_is_audited` (:151-155)
6. `test_manifest_matches_disk` (r4_heavy: for every r4 region, each audit file's sha256 and row count and the per-class
   counts recomputed from it equal the manifest, and n_kept equals the raw catalog's row count; the full replay
   (minutes per region) is re-run for the region with the fewest input rows only, to stay inside the FULL wall time)
7. `test_draft_collection_clause_matches_the_manifest` (reads the (c) clause and the manifest totals; written in Task 3,
   RED against the pre-edit DRAFT)
Expected FULL: base full_15_7j.xml (2,694 = 2,641 P / 53 S / 0 F) + 7 = 2,701 = 2,648 P / 53 S / 0 F (2,700 if Carter's
Q-158R2 is B and test 7 is not written).
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gate; commit the reply + planning set + DEC; audit module (RED first); measure all r4 regions</name>
  <files>.planning/DECISIONS.md, src/python/ta_r4/collector_drop_audit.py, tests/ta_r4/test_collector_drop_audit.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalog_collector_drops.tsv</files>
  <read_first>
    - collect_region_variants.py (all 187 lines); catalog_unique_key.py :21-117; ta_r4_panels.smk :1-20, :90-135
    - data/r4/tmp/w3f/q157/gate_reply.py; data/r4/tmp/w3f/q157/close.sh; data/r4/tmp/w3f/q157/check_tmpl.py
  </read_first>
  <behavior>
    - Tests 1-5 per <new_tests> on small synthetic gzip inputs written in tmp_path (two "trait" files so cross-file
      duplicates occur)
  </behavior>
  <action>
    0. `mkdir -p $Q8`; `git rev-parse HEAD > $Q8/start_15_8a.txt`; confirm 15.7j is committed (`git log` shows its
       close commit and `data/r4/tmp/w3f/q157/full_15_7j.xml` exists; else STOP, 15.8 does not start before 15.7j).
       Assert full_15_7j.xml is identical by id to full_15_7i.xml (`check_tmpl.load(a) == check_tmpl.load(b)`) and record its totals (expected
       2,694 = 2,641 P / 53 S / 0 F). Write `$Q8/gate_157j.sh` and `$Q8/gate_158.sh`, run their negative controls
       (protocol), run them (all five QIDs). Commit 1 (explicit paths): the six reply files as received (`git diff
       --cached --stat` shows them added, sha256 unchanged), the seven 15.8 PLAN files,
       and DEC `DEC-2026-11-24-ta-r4-w3f-15-8-open-items` in .planning/DECISIONS.md quoting the reply file (`cat` +
       `cmp` against the committed file) and the five 2026-11-25 replies, mapping R2→15.8a, R6→15.8b (Q-158R6S),
       R4→15.8c (Q-158DIG), E7 matched rounding + QTL_legacy NaN rule→15.8c2 (Q-158E7R, Q-F3NL), R3→15.8d,
       R5+R7→15.8e (Q-158R7), review→15.8f. Message `docs(ta-r4-W3f): 15.8 planning set + Carter Q-157J reply + DEC (15.8a)`.
    1. `sha256sum` every r4 catalog, raw catalog, `$MAN/catalogs_sha256.tsv` and `$MAN/catalogs_r4_unique_key.tsv`
       into `$Q8/catalog_sha_before_15_8a.txt`. Verify the 8 r4 sumstats against `$MAN/sumstats_r4_sha256.tsv`
       (`ta_r4.verify_inputs`); a mismatch is STOP.
    2. RED: write tests 1-5 and 6 (module absent → ImportError/fail; record the output in `$Q8/red_15_8a.txt`).
    3. `collector_drop_audit.py`: `load_collector()` imports collect_region_variants.py by file path (importlib; the
       legacy file is not edited). `replay(paths, chrom, start, end)` re-implements the collector's loop and post-steps
       line for line, tagging every input row (file, row index, CHR, POS, REF, ALT, SNP_ID) with the step that removes
       it, and returns `(kept_df, dropped_rows)`; `audit_region(region_safe, repo)` runs both the replay and the
       unmodified `collect_variants` on the same inputs, asserts `kept_df.equals(collector_df)` and that
       `kept_df.to_csv(sep="\t", index=False)` is byte-equal to the on-disk raw catalog (raises `ReplayMismatch`
       naming the region otherwise), flags each dropped row against the final catalog's normalized key set (and the
       swapped key), and writes the gzip audit file (columns: CHR POS REF ALT SNP_ID source_file class kept_SNP_ID
       kept_REF kept_ALT key_in_final_catalog swapped_key_in_final_catalog; sorted by CHR, POS, source_file, row
       index). A row matching no class gets `other`. CLI: `python -m ta_r4.collector_drop_audit region --region R` and
       `manifest --out TSV` (assembles the per-region JSON summaries into the manifest; columns per must_haves).
       Tests 1-5 green.
    4. Negative controls (`$Q8/nc_15_8a.txt`): (a) the replay skips the :151-155 step → test 1 and test 5 fail;
       (b) rsid_other_allele_key reported as exact_duplicate → test 2 fails; (c) the key flag uses the un-normalized
       key (raw CHR/REF/ALT strings) → test 4 fails on its case/chr-prefix row; (d) the swapped key counted as the
       exact key → test 4 fails on its swap row. md5-restore after each.
    5. Measure: Slurm array over the r4 regions (`sbatch -p compute -A clintonlab_cpu -q normal -t 02:00:00
       --mem=12G --array=0-<n-1>`), one region per task, writing `$Q8/drops/<region>.json` + the audit file; then
       `manifest`. Any `ReplayMismatch`, any `other` row, or n_input != n_kept + n_dropped in any region is STOP (the
       replay does not describe the collector, or the inputs moved). Test 6 green; time it (`--durations=0`) and record
       the time in the LOG; if it exceeds 15 minutes, reduce its replay to a smaller region before commit 2. Re-hash: catalog_sha_after equals
       catalog_sha_before (cmp). Also measure, for every lost key, whether it is present (exact or swapped alleles at
       the same position) in that region's production panel variant tables (`paths.panel_path(arm, region)` for
       A3_1kg, A3_ukb, AFR661_A3, AFR504_A3, read with the r_coloc Rscript), into `$Q8/lost_keys_in_panels_15_8a.tsv`.
    6. Commit 2: module, tests 1-6, manifest (`test(ta-r4-W3f): collector drop audit, every dropped row classified,
       per-region manifest (15.8a)`). Print the per-region table and the totals line
       `n_input = n_kept + Σ n_dropped` per region and overall.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && bash data/r4/tmp/w3f/q158/gate_158.sh Q-158DIG Q-158R6S Q-158E7R Q-F3NL Q-158R7 && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_collector_drop_audit.py -q -p no:cacheprovider -k "not draft" && cmp data/r4/tmp/w3f/q158/catalog_sha_before_15_8a.txt data/r4/tmp/w3f/q158/catalog_sha_after_15_8a.txt</automated>
  </verify>
  <done>Reply and planning set committed; every r4 region audited with the replay identity holding; manifest committed; catalogs unchanged.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2: Carter decides on lost allele keys (only if n_lost_keys > 0)</name>
  <what-built>catalog_collector_drops.tsv; lost_keys_in_panels_15_8a.tsv; the per-region table</what-built>
  <how-to-verify>
    1. Read the per-region table: drops by class, lost keys, swapped-present, and lost keys present in a production panel.
    2. Answer Q-158R2 (<question>).
    3. Only Carter's own typed reply creates the file. The executor never writes it, and an auto-mode or
       orchestrator-composed "approved" is not a reply. The orchestrator saves it verbatim as
       `$P/W3f-carter-15-8-Q-158R2-reply-<date>.txt` and pins its sha256 in <question>.
  </how-to-verify>
  <files>(none written by the executor)</files>
  <action>Skip if every region has n_lost_keys == 0 (write `lost_keys_total=0` to `$Q8/r2_outcome_15_8a.txt`). Otherwise write `lost_keys_total=<N>` there, print the table and Q-158R2 with the recommendation that the panel measurement supports, and wait. Nothing is written to the DRAFT or any catalog.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && if grep -qx 'lost_keys_total=0' data/r4/tmp/w3f/q158/r2_outcome_15_8a.txt; then echo "no lost keys: Task 2 skipped"; else ls .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158R2-reply-*.txt; fi</automated>
  </verify>
  <done>Either no lost keys (skipped), or Carter's Q-158R2 reply exists with its sha256 pinned here.</done>
  <resume-signal>The reply file exists and its sha256 is pinned in this plan; an auto "approved" is WAIT</resume-signal>
</task>

<task type="auto">
  <name>Task 3: DRAFT (c) clause; FULL vs full_15_7j.xml; records (no push)</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, tests/ta_r4/test_collector_drop_audit.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-SUMMARY.md</files>
  <action>
    1. If Task 2 ran: gate Q-158R2 (staging copy, pinned sha256, label); append it to the DEC; commit. Label B → write
       nothing more to the DRAFT here; record "R2 code fix deferred to a new plan per Carter B" and go to step 3 (the
       manifest and the audit stay; the review row stays OPEN). Label A or no lost keys → step 2.
    2. RED test 7, then the DRAFT script: in (c), replace the clause `the collection step before it keeps one row per
       rsid and omits unnamed variants at a position that carries an rsid, without an audit` (assert unique; if 15.7j
       left other words, use its exact text, quoted in the LOG) with: `the collection step before it keeps one row per
       rsid, omits an unnamed variant at a position that carries an rsid or a second unnamed variant at the same
       position, and every row it omits is listed, with the reason, in an audit file made by replaying that step on
       the same inputs (<N_drop> rows over <n_regions> regions; <N_lost> of them with an allele key that is not in the
       catalog)` with numbers from the manifest (with lost keys under
       Carter A, add the sentence his reply approves; nothing else). Tests 7, test_amendment_text.py and
       test_prelock_pilot_fits.py green. Commit.
    3. `$Q8/close.sh 15_8a` under sbatch (protocol). `$Q8/check_15_8a.py`: base = full_15_7j.xml, NEW = the 7 ids
       (7, or 6 if step 2 did not run: then test 7 is not written and N_new = 6), declared = none, expect = base totals +
       N_new. Records: LOG entry (gate output, premise table, per-region totals, NCs, check output); PLAN-INDEX 15.8a
       row COMPLETE; STATE ★ block (NEXT = 15.8b; NOT PUSHED); SUMMARY with `## Declared spec updates` (none) and
       `## New test ids`. fsck; commit explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8a.py && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import yaml;d=yaml.safe_load(open('config/ta_r4/decision_rules.yaml'));assert d['locked'] is False" && test -z "$(git status --porcelain -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv)"</automated>
  </verify>
  <done>R2 measured and audited; DRAFT (c) states what the audit shows (or Carter's decision is recorded); FULL reconciled; not pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| construction pipeline → public claim "every removed row is audited" | the claim must hold for every step that removes rows |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158a-01 | Tampering | an audit that does not describe the real collector | mitigate | replay kept == unmodified collect_variants and byte-equal to the on-disk raw catalog, per region; class `other` is STOP |
| T-r4-158a-02 | Tampering | silent catalog re-pin | mitigate | sha256 of every catalog before == after; lost keys go to Carter |
| T-r4-158a-03 | Repudiation | reply provenance | mitigate | staging copy cmp + sha256 + exact free text |
</threat_model>

<verification>
- gate_157j.sh passes and its negative controls exit 2; check_15_8a.py passes; catalogs unchanged.
</verification>

<success_criteria>
- Every row the collector removes is in an audit file with a class and counted; any loss of an allele key is
  Carter's decision, not a silent re-pin.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-SUMMARY.md`
</output>
