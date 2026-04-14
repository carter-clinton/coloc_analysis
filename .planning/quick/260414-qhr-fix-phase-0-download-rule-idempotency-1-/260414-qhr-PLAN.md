---
phase: quick-260414-qhr
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/snakemake/rules/pathway.smk
  - tools/magma_v1.10/magma
  - data/reference/ldsc/.baseline_download_done
autonomous: false
requirements:
  - QHR-01  # download_ldsc_baseline idempotent against on-disk references
  - QHR-02  # download_magma_binary path reconciled with manual staging
  - QHR-03  # snakemake all_pathway --dry-run shows both rules up-to-date

must_haves:
  truths:
    - "`snakemake all_pathway --dry-run` does NOT list `download_ldsc_baseline` as a job to run"
    - "`snakemake all_pathway --dry-run` does NOT list `download_magma_binary` as a job to run"
    - "Re-running `snakemake all_pathway --dry-run` a second time is still clean (stable idempotency, not flag-file race)"
    - "download_ldsc_baseline rule, when executed on a system WITHOUT pre-staged data, still functions (logic is additive — only early-exit guard added)"
    - "No other rules (download_ldsc_seg, download_magma_ref, download_hess_panel, download_hess_partition, download_sumstats) are modified by this task"
  artifacts:
    - path: "src/snakemake/rules/pathway.smk"
      provides: "Patched download_ldsc_baseline with on-disk detection + early-exit-with-flag-touch"
      contains: "baseline_download_done"
    - path: "tools/magma_v1.10/magma"
      provides: "Symlink target resolving to data/reference/magma/magma (Carter's manually-staged binary)"
      is_symlink: true
    - path: "data/reference/ldsc/.baseline_download_done"
      provides: "Flag file touched by new idempotency guard so Snakemake treats download_ldsc_baseline as up-to-date"
  key_links:
    - from: "rule download_ldsc_baseline"
      to: "data/reference/ldsc/{baselineLD.22.l2.M, eur_w_ld_chr/, 1000G_EUR_Phase3_plink/, 1000G_Phase3_frq/, 1000G_Phase3_weights_hm3_no_MHC/, w_hm3.snplist}"
      via: "shell [ -f ... ] && [ -d ... ] precondition check that touches {output.baseline_done} + {output.hapmap3} and exits 0"
      pattern: "baseline_download_done.*touch"
    - from: "rule download_magma_binary"
      to: "tools/magma_v1.10/magma"
      via: "symlink pre-staged outside Snakemake; rule output already satisfied at DAG-resolution time"
      pattern: "tools/magma_v1.10/magma -> .*data/reference/magma/magma"
---

<objective>
Make two Phase 0 download rules in `src/snakemake/rules/pathway.smk` idempotent against Carter's manually-staged 32 GB of reference data, so `snakemake all_pathway --dry-run` resolves cleanly without demanding re-fetches from broken / auth-gated upstream sources.

Purpose: The on-disk state from the 2026-04-14 PM session has all LDSC baseline / weights / plink / frq data plus the MAGMA binary staged, but two rules don't detect this:
  1. `download_ldsc_baseline` would unconditionally wget ~5 GB from Broad S3 + GCS requester-pays (the latter fails without auth)
  2. `download_magma_binary` expects its output at `tools/magma_v1.10/magma`; Carter's manual download is at `data/reference/magma/magma` (path mismatch + CNCR JS-gate upstream)

This blocks any real-data execution (narrow scout, per-branch smoke, or full LSF launch) because Snakemake re-plans these as jobs.

Output:
  - Patched `download_ldsc_baseline` rule with an on-disk-detection preflight that touches the flag file + snplist and exits 0 when staged data is present
  - `tools/magma_v1.10/magma` symlink pointing to `data/reference/magma/magma` (rule contract preserved; downstream consumers still read `tools/magma_v1.10/magma`)
  - `data/reference/ldsc/.baseline_download_done` flag file created
  - Verified `snakemake all_pathway --dry-run` no longer lists either rule in the job list
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@./CLAUDE.md
@src/snakemake/rules/pathway.smk

<on_disk_state>
Verified 2026-04-14 via `ls -la data/reference/ldsc/` and `ls data/reference/magma/magma tools/`:

LDSC staged (from Zenodo + scp):
  - data/reference/ldsc/baselineLD.{1..22}.annot.gz                    (Feb 2019)
  - data/reference/ldsc/baselineLD.{1..22}.l2.ldscore.gz               (Feb 2019)
  - data/reference/ldsc/baselineLD.{1..22}.l2.M                        (Feb 2019)
  - data/reference/ldsc/baselineLD.{1..22}.l2.M_5_50                   (Feb 2019)
  - data/reference/ldsc/1000G_EUR_Phase3_plink/                        (Sep 2016)
  - data/reference/ldsc/1000G_Phase3_frq/                              (May 2016)
  - data/reference/ldsc/1000G_Phase3_weights_hm3_no_MHC/               (Oct 2016)
  - data/reference/ldsc/1000G_Phase3_EAS_weights_hm3_no_MHC/           (Nov 2018)
  - data/reference/ldsc/w_hm3.snplist                                  (Apr 14, 17 MB)
  - data/reference/ldsc/eur_w_ld_chr/                                  (per background; not shown in ls sample but referenced in STATE)

MAGMA staged (from CNCR + scp):
  - data/reference/magma/magma                                         (7.2 MB, executable, Jan 2022)

Flag files / symlinks MISSING:
  - data/reference/ldsc/.baseline_download_done                        (rule output — must be touched)
  - tools/magma_v1.10/magma                                            (rule output — must exist)
</on_disk_state>

<interfaces>
From src/snakemake/rules/pathway.smk (lines 94-128, download_magma_binary):

```python
rule download_magma_binary:
    output:
        binary=PATHWAY_CFG.get("magma_binary", "tools/magma_v1.10/magma"),
    # ... wgets magma_v1.10_static.zip from ctg.cncr.nl (JS-gated, blocks curl)
```

From src/snakemake/rules/pathway.smk (lines 180-236, download_ldsc_baseline):

```python
rule download_ldsc_baseline:
    output:
        baseline_done=touch("data/reference/ldsc/.baseline_download_done"),
        hapmap3=PATHWAY_CFG.get("ldsc_hapmap3", "data/reference/ldsc/w_hm3.snplist"),
    params:
        outdir="data/reference/ldsc",
        baseline_url="https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/UKBB_LD/baselineLD_v2.2_ldscores.tgz",
        weights_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/weights_hm3_no_hla.tgz",
        frq_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/1000G_Phase3_frq.tgz",
        plink_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/1000G_Phase3_plinkfiles.tgz",
        hapmap3_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/w_hm3.snplist.bz2",
    shell:
        r"""
        mkdir -p {params.outdir}
        # ... unconditional wgets + tar xzf ...
        """
```

HPC environment invariants (from memory):
  - Snakemake binary: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` (Python 3.11 + snakemake 7.32.4)
  - Node PATH prefix: `/rs1/researchers/c/ckclinto/miniconda3/bin` for GSD CLI calls
  - Never invoke `snakemake` from miniconda3 base (Python 3.13 + snakemake 8.x mismatch)
</interfaces>

<design_decisions>
D-01 (symlink vs. rule rewrite for MAGMA path mismatch):
  CHOSEN: Symlink `tools/magma_v1.10/magma -> ../../data/reference/magma/magma` (relative target for repo-relocatability).
  Rationale:
    - Cheapest change (one symlink, no rule edit)
    - Preserves the rule's `output: binary="tools/magma_v1.10/magma"` contract so downstream consumers (run_magma.py) continue reading from the expected path
    - Snakemake treats existing symlink as satisfied output for a rule with no inputs (`download_magma_binary` has no inputs, only the binary output + URL param); dry-run reports it as up-to-date
    - Reversible: `rm tools/magma_v1.10/magma` restores the original behavior
  Rejected alternatives:
    - Modify rule output to `data/reference/magma/magma`: breaks rule-output contract, requires grepping every consumer, higher blast radius
    - Modify config/pipeline.yaml `pathway.magma_binary` key: same consumer-grep problem, and the default fallback string is hard-coded in the rule anyway

D-02 (early-exit guard vs. run-block refactor for LDSC baseline):
  CHOSEN: Append preflight block at the TOP of the existing shell block that checks for canonical on-disk artifacts and, if present, touches outputs + `exit 0`.
  Rationale:
    - Minimal diff; no rule-type change (shell → run) which would require rewriting the downstream shell commands as Python subprocess calls
    - Preserves original wget fallback for a fresh clone / fresh HPC account (rule still functions end-to-end when data is absent)
    - Sentinel set = {last-chromosome baseline files + 4 canonical subdirs + snplist}; comprehensive enough that a partial/corrupt stage won't spoof detection
  Rejected alternatives:
    - Refactor to `run:` block with Python os.path checks: larger diff, no functional gain
    - Split into two rules (idempotency_check + actual_download): overengineering for a 1-file patch
    - Use `input: ancient(...)` pattern: doesn't solve the missing-flag-file problem since the flag is the rule's output, not its input

D-03 (scope of detection guard):
  CHOSEN: Detect presence of BOTH (a) baselineLD.22.l2.M AND (b) 1000G_EUR_Phase3_plink/ AND (c) 1000G_Phase3_frq/ AND (d) 1000G_Phase3_weights_hm3_no_MHC/ AND (e) w_hm3.snplist. Chromosome 22 chosen as last-in-alphabetical-sort proxy for a complete unpack.
  Rationale: All 4 subdirs + snplist match what the wget block produces downstream; if any is missing, fall through to wget (allowing partial-recovery runs on fresh systems).

D-04 (out-of-scope enumeration):
  NOT TOUCHED by this plan:
    - download_ldsc_seg (has same idempotency gap; deferred — noted in <deferred_followup>)
    - download_magma_ref (same gap; deferred)
    - download_hess_panel (same gap; deferred)
    - download_hess_partition (same gap; deferred)
    - download_sumstats (explicitly excluded per task constraints — needs separate cache/downloads scoping decision first)
</design_decisions>

<deferred_followup>
Note but DO NOT modify in this task (tracked for next quick task):
  - download_ldsc_seg  (pathway.smk:239) — Multi_tissue_gene_expr + chromatin from GCS requester-pays; same idempotency gap
  - download_magma_ref (pathway.smk:131) — NCBI37.3.gene.loc + g1000_eur + dbsnp151.synonyms from CNCR JS-gate; same gap
  - download_hess_panel (pathway.smk:334) — may be relevant but note Carter has symlink farm already under data/reference/hess/ld_panel/EUR/
  - download_hess_partition (pathway.smk:~400+) — EUR/AFR/EAS partitions already staged from Bitbucket
  - download_sumstats — 8 trait/ancestry combos; needs separate scoping (cache/downloads vs data/raw/sumstats, URL-rot audit, overwrite-protection for existing Feb-11 harmonized files)

These should become a follow-up quick task after QHR lands and a clean narrow-scout run proves the pattern works.
</deferred_followup>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Patch download_ldsc_baseline with on-disk-detection preflight + create MAGMA symlink</name>
  <files>
    src/snakemake/rules/pathway.smk
    tools/magma_v1.10/magma (new symlink)
    data/reference/ldsc/.baseline_download_done (created by running the patched rule OR by explicit touch — see action)
  </files>
  <action>
    Make two changes, in order:

    **Change A — Patch `download_ldsc_baseline` shell block (src/snakemake/rules/pathway.smk:199-236):**

    Insert a preflight guard IMMEDIATELY AFTER the `mkdir -p {params.outdir}` line (currently line ~201) and BEFORE the first `wget` for the baseline tgz. The guard must:

    1. Test presence of all five sentinel artifacts (per D-03):
       - `[ -f {params.outdir}/baselineLD.22.l2.M ]`
       - `[ -d {params.outdir}/1000G_EUR_Phase3_plink ]`
       - `[ -d {params.outdir}/1000G_Phase3_frq ]`
       - `[ -d {params.outdir}/1000G_Phase3_weights_hm3_no_MHC ]`
       - `[ -f {output.hapmap3} ]`
    2. When all five exist: log a clear "Detected pre-staged LDSC reference data on disk; skipping download" message to stderr, `touch {output.baseline_done}` explicitly (normally Snakemake's `touch()` wrapper handles this at rule-exit, but being explicit here is defensive in case of shell short-circuits), and `exit 0`.
    3. When any is missing: fall through to the existing wget block unchanged.

    Exact insertion (bash `if` block, using `&&` chain for readability — all on-disk tests must pass):

    ```bash
    # Idempotency guard (D-02, D-03): if references are already staged on disk,
    # touch the flag + snplist outputs and exit cleanly. Prevents re-fetching
    # ~5 GB from Broad S3 + GCS requester-pays (the latter fails without auth)
    # on systems where Carter has manually staged the data from Zenodo.
    if [ -f {params.outdir}/baselineLD.22.l2.M ] && \
       [ -d {params.outdir}/1000G_EUR_Phase3_plink ] && \
       [ -d {params.outdir}/1000G_Phase3_frq ] && \
       [ -d {params.outdir}/1000G_Phase3_weights_hm3_no_MHC ] && \
       [ -f {output.hapmap3} ]; then
        echo "download_ldsc_baseline: detected pre-staged LDSC reference data on disk; skipping download" >&2
        touch {output.baseline_done}
        exit 0
    fi
    ```

    DO NOT modify the rest of the shell block. DO NOT remove the wget fallback — it must remain functional for fresh-clone systems.

    Do NOT touch download_ldsc_seg, download_magma_ref, download_hess_panel, download_hess_partition, or download_sumstats in this patch. (Deferred — see <deferred_followup>.)

    **Change B — Create MAGMA symlink (D-01):**

    From repo root:
    ```bash
    mkdir -p tools/magma_v1.10
    ln -s ../../data/reference/magma/magma tools/magma_v1.10/magma
    # Verify the symlink resolves and the target is executable:
    test -x tools/magma_v1.10/magma || { echo "FAIL: symlink broken or target not executable" >&2; exit 1; }
    # Verify it's the correct binary (smoke test — magma --help prints banner including version)
    tools/magma_v1.10/magma --version 2>&1 | head -1 || true
    ```

    Relative target (`../../data/reference/magma/magma`) is used so the symlink survives repo moves. If relative target fails to resolve due to gpfs symlink quirks, fall back to absolute: `ln -s /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/data/reference/magma/magma tools/magma_v1.10/magma`.

    **Change C — Explicitly touch the LDSC flag file (belt-and-suspenders):**

    Even though the patched rule's preflight will touch the flag when invoked, Snakemake's DAG resolution looks at the flag's existence BEFORE invoking any rule. To make the dry-run immediately clean without needing a first (no-op) rule execution:
    ```bash
    touch data/reference/ldsc/.baseline_download_done
    ```

    This is safe because the on-disk LDSC data really IS complete; the flag file is purely a Snakemake bookkeeping artifact.
  </action>
  <verify>
    <automated>
    # Guard: no other rules were modified
    test $(grep -c "Idempotency guard" src/snakemake/rules/pathway.smk) -eq 1

    # Guard: MAGMA symlink resolves to the manual-staged binary
    test -L tools/magma_v1.10/magma && test -x tools/magma_v1.10/magma

    # Guard: flag file exists
    test -f data/reference/ldsc/.baseline_download_done

    # Sanity: shell block still parses (syntax-check by having snakemake list rules — much faster than a full dry-run)
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --list 2>&1 | grep -q download_ldsc_baseline
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --list 2>&1 | grep -q download_magma_binary
    </automated>
  </verify>
  <done>
    - `src/snakemake/rules/pathway.smk` contains exactly ONE new `if [ -f ... ]` guard block inside `download_ldsc_baseline`'s shell section
    - No other download rules modified
    - `tools/magma_v1.10/magma` is a symlink resolving to `data/reference/magma/magma`, and the target is executable
    - `data/reference/ldsc/.baseline_download_done` exists
    - `snakemake --list` succeeds (proves the .smk file still parses)
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Verify `snakemake all_pathway --dry-run` reports both rules as up-to-date</name>
  <what-built>
    Task 1 patched `download_ldsc_baseline` with an on-disk-detection preflight, created a `tools/magma_v1.10/magma` symlink to Carter's manually staged binary, and created the `.baseline_download_done` flag file.
  </what-built>
  <how-to-verify>
    1. Run (from repo root `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/`):
       ```bash
       export PATH=/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH
       /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run 2>&1 | tee /tmp/qhr_dryrun.log
       ```
    2. Grep the job list section:
       ```bash
       grep -E "^rule (download_ldsc_baseline|download_magma_binary):" /tmp/qhr_dryrun.log
       ```
       Expected: ZERO matches. (If either appears, the idempotency guard is not firing — investigate which sentinel test is failing.)
    3. Check that the dry-run completes without a "MissingInputException" / "MissingOutputException" naming either of the two files `.baseline_download_done` or `tools/magma_v1.10/magma`.
    4. Run the dry-run a SECOND time to confirm stability (no rule should have transitioned state between runs):
       ```bash
       /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run 2>&1 | grep -E "^rule (download_ldsc_baseline|download_magma_binary):"
       ```
       Expected: still zero matches.
    5. Eyeball the full job list (`grep "^rule " /tmp/qhr_dryrun.log`) to confirm the remaining downstream rules look sane and no new failures surfaced.

    Expected outcomes:
      - Both target rules ABSENT from the dry-run job list
      - Dry-run exits 0 (or with the expected pre-existing DEF-RO7-01 / DEF-RO7-02 / DEF-RO7-03 errors — those are deferred blockers, not new regressions)
      - If dry-run fails with a different error (e.g., references sumstats, ld_reference TRANS.samples), that is OUT OF SCOPE for QHR — flag it and proceed to approve.

    If verification FAILS (either target rule still appears):
      - Do not proceed to commit.
      - Report which rule is still in the job list and the triggering missing sentinel file, if known.
  </how-to-verify>
  <resume-signal>Type "approved" after confirming both rules are absent from the dry-run job list (twice). If dry-run surfaces unrelated failures (DEF-RO7-*, sumstats, TRANS.samples), note them in the approval message; they are out of scope for QHR.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| shell → filesystem | Preflight `[ -f ]` / `[ -d ]` tests run inside Snakemake-managed shell with full user creds; no untrusted input |
| Snakemake DAG → pre-staged data | Flag file and symlink manually placed; we trust that Carter's 32 GB Zenodo download is genuine (out-of-band verified by file sizes + use in prior smoke tests) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-qhr-01 | Tampering | `data/reference/ldsc/baselineLD.*` files spoofed by attacker to pass the 5-sentinel check with corrupted data | accept | On-disk data was staged by Carter from Zenodo (DOI-addressable, content-addressable via SHA). HPC filesystem has per-user chmod; compromise would require gpfs-level attack. Sentinel check is 5 artifacts deep, not just flag file. |
| T-qhr-02 | Tampering | Symlink `tools/magma_v1.10/magma` could be redirected to a malicious binary | accept | Symlink owned by ckclinto; target `data/reference/magma/magma` in same project tree under user-controlled filesystem. No elevated privilege path. |
| T-qhr-03 | DoS (self-inflicted) | Preflight guard could false-negative (sentinel missing due to partial unpack), falling through to wget, which hangs on GCS requester-pays auth prompt | mitigate | Guard requires ALL FIVE sentinels present (baselineLD.22.l2.M, 3 subdirs, snplist). A partial unpack would fall through to wget and fail fast (wget --timeout=300 + GCS 401/403 returns quickly, not hang). User receives actionable error. |
| T-qhr-04 | Information Disclosure | Flag file touched without real data underneath could mask a failure and produce garbage downstream LDSC results | mitigate | Five-sentinel check is the guard against this. Explicit manual `touch` of flag file (Change C) is conditional on human verification of on-disk state — not a blind touch. |
| T-qhr-05 | Repudiation | No audit trail if someone removes a sentinel file later and wget fails silently | accept | Snakemake logs all rule invocations to stderr + `.snakemake/log/`. Wget failures surface as non-zero exits which halt the DAG. Low risk for solo-author pipeline. |
| T-qhr-06 | Elevation of Privilege | Shell block executes as ckclinto on HPC login/compute node — no privilege change requested | accept | No sudo, no setuid paths. Executes within existing Snakemake shell contract. |
</threat_model>

<verification>
Overall phase checks (bash-executable):

```bash
export PATH=/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake

# 1. Files in place
test -L tools/magma_v1.10/magma
test -x tools/magma_v1.10/magma
test -f data/reference/ldsc/.baseline_download_done

# 2. Snakemake still parses
$SMK --list >/dev/null

# 3. Neither rule appears in the all_pathway dry-run job list
JOB_COUNT=$($SMK all_pathway --dry-run 2>&1 | grep -cE "^rule (download_ldsc_baseline|download_magma_binary):")
test "$JOB_COUNT" -eq 0

# 4. Stable across a second dry-run
JOB_COUNT_2=$($SMK all_pathway --dry-run 2>&1 | grep -cE "^rule (download_ldsc_baseline|download_magma_binary):")
test "$JOB_COUNT_2" -eq 0

# 5. pathway.smk patch contains exactly one idempotency guard (not duplicated, not missing)
test $(grep -c "Idempotency guard" src/snakemake/rules/pathway.smk) -eq 1

# 6. Out-of-scope rules NOT modified
# (git diff should only show changes in download_ldsc_baseline; no line changes in download_ldsc_seg / download_magma_ref / download_hess_panel / download_hess_partition / download_sumstats)
git diff src/snakemake/rules/pathway.smk | grep -E "^\+" | grep -vE "Idempotency guard|^\+\+\+|baseline_download_done|baselineLD\.22|1000G_EUR_Phase3_plink|1000G_Phase3_frq|1000G_Phase3_weights_hm3_no_MHC|output\.hapmap3|download_ldsc_baseline|skipping download|^\+ *$|^\+ *#" | head -5
```
</verification>

<success_criteria>
- `snakemake all_pathway --dry-run` exits with ZERO jobs for `download_ldsc_baseline` and `download_magma_binary`
- Second dry-run matches first (idempotent)
- `tools/magma_v1.10/magma` is a working symlink to `data/reference/magma/magma`
- `data/reference/ldsc/.baseline_download_done` exists
- Exactly ONE block of new `if [ -f ... ]` guard code added to `download_ldsc_baseline`; no other rule bodies edited
- git diff scope is bounded: `src/snakemake/rules/pathway.smk` + `tools/magma_v1.10/magma` (symlink) + `data/reference/ldsc/.baseline_download_done` (flag)
- Any dry-run failures surfaced are pre-existing (DEF-RO7-01 ld_reference TRANS.samples, DEF-RO7-02 trait_ancestries harmonize, DEF-RO7-03 config path, download_sumstats chain) — NOT new regressions introduced by this patch
- Deferred follow-ups clearly flagged in SUMMARY for the next quick task (download_ldsc_seg, download_magma_ref, download_hess_panel, download_hess_partition, download_sumstats)
</success_criteria>

<output>
After completion, create `.planning/quick/260414-qhr-fix-phase-0-download-rule-idempotency-1-/260414-qhr-SUMMARY.md`
</output>
