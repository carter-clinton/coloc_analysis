---
plan_id: m1-01-portal-fetches-and-aragam-route
phase: m1
plan: 01
type: execute
wave: 1
depends_on: [m1-00-preflight-and-environment]
autonomous: false
requirements: [REQ-PUBLIC-DATA-ONLY, REQ-PATH-PARAMETERIZATION, REQ-TRAIT-INVENTORY]
objective: "Fetch the remaining 17 portal-gated sumstats rows (Yengo 2018, Loh 2022 x2, PAGE BMI-AFR, DIAMANTE x4, GIGASTROKE x5 post-D-02, GBMI x3, MAGIC x6, Giri per D-06) via bin/download_sumstats_v2.sh extension; unzip Aragam 2022 with D-03 routing; freeze primary raw SHA-256 manifest after all 27+N files land."
files_modified:
  - bin/download_sumstats_v2.sh
  - config/download_manifest_m1_portal.tsv
  - src/snakemake/rules/m1_download.smk
  - src/python/freeze_sha256_manifest.py
  - data/raw/sumstats_v2/GIANT2018/BMI/EUR/
  - data/raw/sumstats_v2/Loh2022/BMI/EUR/
  - data/raw/sumstats_v2/Loh2022/BMI/AFR/
  - data/raw/sumstats_v2/PAGE2019/BMI/AFR/
  - data/raw/sumstats_v2/DIAMANTE2022/T2D/
  - data/raw/sumstats_v2/GIGASTROKE2022/stroke/
  - data/raw/sumstats_v2/GBMI2022/asthma/
  - data/raw/sumstats_v2/MAGIC2021/HbA1c/
  - data/raw/sumstats_v2/Aragam2022/
  - data/raw/sumstats_v2/sha256_manifest.tsv
  - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md
must_haves:
  truths:
    - "Every row of SUMSTATS-UPGRADE.tsv with status=to_download has either landed on disk OR is marked DEFERRED with documented reason"
    - "Aragam 2022 ZIP has been unpacked and AFR branch decision is reflected in the raw tree"
    - "Raw SHA-256 manifest at data/raw/sumstats_v2/sha256_manifest.tsv is reproducible across re-runs"
    - "Snakemake download rule is path-parameterized (no hardcoded /rs1 /gpfs_common in rule text)"
  artifacts:
    - path: "bin/download_sumstats_v2.sh"
      provides: "Extended xargs -P 5 driver covering Wave 1 portal rows per feedback_parallel_downloads memory"
    - path: "config/download_manifest_m1_portal.tsv"
      provides: "One row per portal source (17 rows expected): url, target_dir, expected_filename, required_cookie, sha256_expected_if_known"
    - path: "src/snakemake/rules/m1_download.smk"
      provides: "Path-parameterized Snakemake download rules invoking bin/download_sumstats_v2.sh per manifest row"
    - path: "src/python/freeze_sha256_manifest.py"
      provides: "Deterministic sorted-output hash manifest writer — re-run yields byte-identical TSV"
    - path: "data/raw/sumstats_v2/sha256_manifest.tsv"
      provides: "Frozen provenance artifact — raw fetch SHA-256 manifest per D-13 primary (OSF paste slot)"
    - path: "data/raw/sumstats_v2/Aragam2022/"
      provides: "Unzipped contents; AFR file present per D-03 branch (a) OR absent with Klarin 2018 fallback plan per branch (b)"
  key_links:
    - from: "src/snakemake/rules/m1_download.smk"
      to: "bin/download_sumstats_v2.sh"
      via: "shell: bash driver invocation per manifest row"
      pattern: "bin/download_sumstats_v2\\.sh"
    - from: "src/python/freeze_sha256_manifest.py"
      to: "data/raw/sumstats_v2/"
      via: "walk + sort + hash"
      pattern: "sha256sum|hashlib"
    - from: "bin/download_sumstats_v2.sh"
      to: "config/download_manifest_m1_portal.tsv"
      via: "read manifest rows; xargs -P 5 fetch_one"
      pattern: "xargs.*-P.*5"
---

<objective>
Close the Wave 0 → Wave 2 gap by landing all portal-gated raw sumstats files on disk. Extend `bin/download_sumstats_v2.sh` (the proven xargs -P 5 idempotent driver that already landed 27 files at 40.4 GB) with a new manifest covering the 17 remaining rows: Yengo 2018 BMI EUR, Loh 2022 BMI EUR + AFR, PAGE 2019 BMI AFR, DIAMANTE 4 rows (TRANS/EUR/EAS/SAS; AFR + HIS deferred per D-10 notes), GIGASTROKE 4 rows per D-02 integer lock (TRANS/EUR/AFR/EAS), GBMI 3 rows (MULTI/EUR/AFR), MAGIC 6 rows (TRANS/EUR/AFR/EAS/SAS/HIS) if Wave 0 FTP probe passed, and Giri 2019 MVP per D-06 disposition. Unzip the already-landed Aragam 2022 CARDIoGRAM ZIP and route per D-03 branch outcome from Wave 0. After all fetches complete, freeze the primary SHA-256 manifest at `data/raw/sumstats_v2/sha256_manifest.tsv` — this is the OSF amendment paste-ready artifact per D-13.

Purpose: Wave 2 harmonizers cannot start their per-source DAG until raw files exist. The manifest-driven driver gives Wave 2 the harmonize-as-ready parallelization policy (D-14): each per-source file that lands triggers its own harmonizer rule in Wave 2 without gating on the slowest fetch. The frozen SHA-256 manifest is the M1 closeout deliverable that pastes into OSF-AMENDMENT-TEXT-2026-04-22.md placeholder 1 (Carter performs the osf.io web-UI action at M2 gate per Amendment §9.1).
Output: An extended `bin/download_sumstats_v2.sh`, a new `config/download_manifest_m1_portal.tsv`, one new `src/snakemake/rules/m1_download.smk` file with path-parameterized rules, a `src/python/freeze_sha256_manifest.py` deterministic hasher, the 17 new raw subtrees under `data/raw/sumstats_v2/`, the Aragam ZIP unpacked, and the frozen primary SHA-256 manifest.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-CONTEXT.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-VALIDATION.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-00-preflight-and-environment-PLAN.md
@.planning/amendments/SUMSTATS-UPGRADE.tsv
@.planning/amendments/SUMSTATS-UPGRADE.md
@.planning/amendments/SUMSTATS-MANUAL-FETCH.md
@.planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md
@.planning/amendments/SUMSTATS-SCRIPTED-FETCH-COMPLETE.md
@bin/download_sumstats_v2.sh
@config/bsub_wrapper.sh
@config/pipeline.yaml
@src/snakemake/rules/sumstats.smk
@CLAUDE.md

<interfaces>
<!-- Proven patterns from bin/download_sumstats_v2.sh + project memories. Executor should mirror verbatim. -->

From bin/download_sumstats_v2.sh (existing idempotent driver — 27 files landed):
```bash
fetch_one() {
  local url="$1" target_dir="$2" filename="$3"
  mkdir -p "$target_dir"
  local target="$target_dir/$filename"
  if [ -s "$target" ]; then
    echo "[skip] $target exists"
    return 0
  fi
  curl --connect-timeout 30 --max-time 7200 -fsSL "$url" -o "$target.partial" \
    && mv "$target.partial" "$target"
}
export -f fetch_one

cat "$MANIFEST" | xargs -P 5 -I {} bash -c 'fetch_one {}'
```
Manifest format: tab-separated `url\ttarget_dir\tfilename` per row.

From /home/ckclinto/.claude/projects/.../feedback_parallel_downloads.md:
- xargs -P 5 saturates bandwidth on NCSU HPC; don't exceed per institutional bandwidth guidance
- Always use login node for large fetches; LSF compute node egress may be rate-limited

From /home/ckclinto/.claude/projects/.../feedback_url_rot_workarounds.md:
- Broad `data.broadinstitute.org` occasionally 403s → fall back to Zenodo mirrors
- UCLA Box / CNCR / EBI broken URLs → use NCBI or Bitbucket alternates where documented in SUMSTATS-UPGRADE.md §5

From /home/ckclinto/.claude/projects/.../feedback_lsf_queues.md:
- Portal fetches go on `standard` queue (2880 min wall max) via bsub_wrapper.sh
- Giant ZIP extractions with possible multi-GB decompression → `long` queue (14400 min) if needed

Expected raw-tree layout (config/pipeline.yaml paths.raw_sumstats_v2 = "data/raw/sumstats_v2"):
```
data/raw/sumstats_v2/
├── GLGC2021/                 (24 files — ALREADY LANDED)
├── CKDGen2019/               (2 files — ALREADY LANDED)
├── Aragam2022/               (1 ZIP — ALREADY LANDED; Wave 0 wrote manifest; this plan unzips)
├── GIANT2018/BMI/EUR/        (Yengo 2018 — 1 file)
├── Loh2022/BMI/{EUR,AFR}/    (2 files)
├── PAGE2019/BMI/AFR/         (1 file — D-05 conditional)
├── DIAMANTE2022/T2D/{TRANS,EUR,EAS,SAS}/  (4 files; AFR+HIS dua_pending)
├── GIGASTROKE2022/stroke/{TRANS,EUR,AFR,EAS}/  (4 files per D-02 integer lock)
├── GBMI2022/asthma/{MULTI,EUR,AFR}/  (3 files)
├── MAGIC2021/HbA1c/{TRANS,EUR,AFR,EAS,SAS,HIS}/  (6 files — only if Wave 0 FTP probe passed)
└── MVP2019/BP/AFR/           (1 file or DEFERRED per D-06 disposition)
```

Per CLAUDE.md + REQ-PATH-PARAMETERIZATION: NEVER hardcode `/rs1/researchers` or `/gpfs_common` in rule text. Always route through `config["paths"][...]`.
</interfaces>
</context>

<tasks>

<task id="m1-01-T1" type="auto" tdd="true">
  <name>Task 1: Extend download driver + author path-parameterized Snakemake download rules + deterministic SHA-256 freezer</name>
  <files>
    bin/download_sumstats_v2.sh,
    config/download_manifest_m1_portal.tsv,
    src/snakemake/rules/m1_download.smk,
    src/python/freeze_sha256_manifest.py,
    tests/m1/test_freeze_sha256_manifest.py
  </files>
  <read_first>
    - bin/download_sumstats_v2.sh (entire file — copy fetch_one helper + xargs pattern verbatim; append new manifest reader)
    - .planning/amendments/SUMSTATS-UPGRADE.tsv (all rows with status=to_download — copy url + expected_filename verbatim)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH.md (portal protocols for DIAMANTE cookie, GBMI, MAGIC FTP fallback)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md (Wave 0 probe outcomes — MAGIC FTP pass/fail drives MAGIC row inclusion vs fallback)
    - src/snakemake/rules/sumstats.smk (existing path-parameterized pattern for raw_sumstats)
    - config/pipeline.yaml (confirm `paths.raw_sumstats_v2` key; add if absent)
    - /home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/feedback_url_rot_workarounds.md (Zenodo/NCBI/Bitbucket alternates)
  </read_first>
  <behavior>
    - bin/download_sumstats_v2.sh gains a `--manifest <path>` flag that accepts the new TSV; default remains the pre-existing in-script manifest for backward compat
    - DIAMANTE rows get a `-b "$DIAMANTE_COOKIE"` curl augment (cookie persistence documented in SUMSTATS-MANUAL-FETCH.md) — the env var resolution is a one-line helper; if unset, driver emits "MANUAL ACTION REQUIRED" and exits 0 on that row (does NOT fail the whole batch)
    - If Wave 0 probe 1 (MAGIC FTP egress) returned FAIL, the manifest emits 0 MAGIC rows and the download rule writes 6 `.deferred` placeholder files with content "MAGIC FTP egress blocked at Wave 0; fall back to EBI mirror or login-node proxy per SUMSTATS-UPGRADE §5 Tier 1"
    - config/download_manifest_m1_portal.tsv columns: url, target_dir, filename, requires_cookie_env, sha256_expected, source_tag, trait, ancestry, consortium, year — 17 target rows (minus MAGIC if FTP fail; minus row 13 if D-06 primary fail)
    - src/snakemake/rules/m1_download.smk rule invokes bin/download_sumstats_v2.sh --manifest config/download_manifest_m1_portal.tsv; one rule emits a flag file per source_tag (e.g. touch data/raw/sumstats_v2/.download_complete.<source_tag>) so downstream Wave 2 rules gate on the flag rather than on individual files (harmonize-as-ready per D-14)
    - src/python/freeze_sha256_manifest.py walks a root dir, computes sha256 per file, sorts by (relative_path), emits `<rel_path>\t<sha256>\t<bytes>\t<mtime_iso>` TSV. Crucially deterministic — second run produces byte-identical TSV modulo mtime column (which is excluded from a `--no-mtime` flag used for the OSF paste artifact)
    - tests/m1/test_freeze_sha256_manifest.py creates a 3-file fixture tree, calls freeze_sha256_manifest(root, out_tsv, with_mtime=False), asserts (a) 3 rows, (b) second run is byte-identical, (c) row order is lexicographic on relative path
  </behavior>
  <action>
    1. Copy bin/download_sumstats_v2.sh; add `--manifest` flag parsing (defaults to the current inline manifest). Add support for `DIAMANTE_COOKIE` env var: if set, `fetch_one` prepends `-b "$DIAMANTE_COOKIE"` to the curl call when the row's `requires_cookie_env` column equals `DIAMANTE_COOKIE`. If env var missing but required, emit `echo "MANUAL ACTION: export DIAMANTE_COOKIE=..." ; return 0` rather than fail.

    2. Author config/download_manifest_m1_portal.tsv with 17 rows (minus deferrals). Column order: `source_tag\turl\ttarget_dir\tfilename\trequires_cookie_env\tsha256_expected\ttrait\tancestry\tconsortium\tyear`. Reference rows (paste verbatim from SUMSTATS-UPGRADE.tsv + apply D-02 integer-locked GIGASTROKE names from Wave 0):

    ```
    source_tag  url  target_dir  filename  requires_cookie_env  sha256_expected  trait  ancestry  consortium  year
    GIANT2018_BMI_EUR  https://portals.broadinstitute.org/collaboration/giant/images/2/2f/Meta-analysis_Locke_et_al%2BUKBiobank_2018_UPDATED.txt.gz  data/raw/sumstats_v2/GIANT2018/BMI/EUR  Meta-analysis_Locke_et_al+UKBiobank_2018_UPDATED.txt.gz  NONE  UNKNOWN  bmi  EUR  GIANT-UKBB  2018
    Loh2022_BMI_EUR  PENDING_D01_ACCESSION  data/raw/sumstats_v2/Loh2022/BMI/EUR  Loh2022_BMI_EUR.tsv.gz  NONE  UNKNOWN  bmi  EUR  GIANT-23andMe  2022
    Loh2022_BMI_AFR  PENDING_D01_ACCESSION  data/raw/sumstats_v2/Loh2022/BMI/AFR  Loh2022_BMI_AFR.tsv.gz  NONE  UNKNOWN  bmi  AFR  GIANT-23andMe  2022
    PAGE2019_BMI_AFR  https://www.ebi.ac.uk/gwas/publications/31217584  data/raw/sumstats_v2/PAGE2019/BMI/AFR  PAGE_BMI_AFR_ALL_2019-06.tsv  NONE  UNKNOWN  bmi  AFR  PAGE  2019
    DIAMANTE2022_T2D_TRANS  https://diagram-consortium.org/downloads/DIAMANTE-TA.sumstat.txt.gz  data/raw/sumstats_v2/DIAMANTE2022/T2D/TRANS  DIAMANTE-TA.sumstat.txt.gz  DIAMANTE_COOKIE  UNKNOWN  t2d  TRANS  DIAMANTE  2022
    DIAMANTE2022_T2D_EUR  https://diagram-consortium.org/downloads/DIAMANTE-EUR.sumstat.txt.gz  data/raw/sumstats_v2/DIAMANTE2022/T2D/EUR  DIAMANTE-EUR.sumstat.txt.gz  DIAMANTE_COOKIE  UNKNOWN  t2d  EUR  DIAMANTE  2022
    DIAMANTE2022_T2D_EAS  https://diagram-consortium.org/downloads/DIAMANTE-EAS.sumstat.txt.gz  data/raw/sumstats_v2/DIAMANTE2022/T2D/EAS  DIAMANTE-EAS.sumstat.txt.gz  DIAMANTE_COOKIE  UNKNOWN  t2d  EAS  DIAMANTE  2022
    DIAMANTE2022_T2D_SAS  https://diagram-consortium.org/downloads/DIAMANTE-SAS.sumstat.txt.gz  data/raw/sumstats_v2/DIAMANTE2022/T2D/SAS  DIAMANTE-SAS.sumstat.txt.gz  DIAMANTE_COOKIE  UNKNOWN  t2d  SAS  DIAMANTE  2022
    GIGASTROKE2022_stroke_TRANS  https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/<GCST-range>/<GCST-int-per-D-02>/  data/raw/sumstats_v2/GIGASTROKE2022/stroke/TRANS  <GCST-int>_buildGRCh37.tsv.gz  NONE  UNKNOWN  stroke  TRANS  GIGASTROKE  2022
    GIGASTROKE2022_stroke_EUR  <ditto>  data/raw/sumstats_v2/GIGASTROKE2022/stroke/EUR  <GCST-int>_EUR_AS.tsv.gz  NONE  UNKNOWN  stroke  EUR  GIGASTROKE  2022
    GIGASTROKE2022_stroke_AFR  <ditto>  data/raw/sumstats_v2/GIGASTROKE2022/stroke/AFR  <GCST-int>_AA_AS.tsv.gz  NONE  UNKNOWN  stroke  AFR  GIGASTROKE  2022
    GIGASTROKE2022_stroke_EAS  <ditto>  data/raw/sumstats_v2/GIGASTROKE2022/stroke/EAS  <GCST-int>_EAS_AS.tsv.gz  NONE  UNKNOWN  stroke  EAS  GIGASTROKE  2022
    GBMI2022_asthma_MULTI  https://www.globalbiobankmeta.org/resources  data/raw/sumstats_v2/GBMI2022/asthma/MULTI  Asthma_Bothsex_inv_var_meta_GBMI_052021.txt.gz  NONE  UNKNOWN  asthma  MULTI  GBMI  2022
    GBMI2022_asthma_EUR  <ditto>  data/raw/sumstats_v2/GBMI2022/asthma/EUR  Asthma_Bothsex_inv_var_meta_GBMI_EUR_052021.txt.gz  NONE  UNKNOWN  asthma  EUR  GBMI  2022
    GBMI2022_asthma_AFR  <ditto>  data/raw/sumstats_v2/GBMI2022/asthma/AFR  Asthma_Bothsex_inv_var_meta_GBMI_AFR_052021.txt.gz  NONE  UNKNOWN  asthma  AFR  GBMI  2022
    ```

    Then conditional rows:
    - If Wave 0 probe 1 recorded MAGIC FTP pass → add 6 MAGIC rows; else omit
    - If Wave 0 probe 2 recorded Giri 2019 summary availability → add Giri row; else omit (Wave 1 rule writes `.deferred` placeholder)

    N1 fix — handle PENDING_D01_ACCESSION sentinel: extend bin/download_sumstats_v2.sh fetch_one() driver to detect the sentinel and skip-with-marker rather than fail. Add near the top of fetch_one():
    ```bash
    if [[ "$url" == PENDING_* ]]; then
        mkdir -p "$target_dir"
        touch "$target_dir/.deferred"
        echo "[DEFERRED] $source_tag: $url (D-01 accession unresolved; Wave 1 .deferred placeholder written)"
        return 0
    fi
    ```
    This is consistent with the existing Giri / MAGIC-FTP-fail deferral pattern (downstream Wave 2 harmonize rules check for `.deferred` and emit their own deferred placeholder). When Carter resolves the D-01 GWAS-Catalog accession at any future point, edit the manifest TSV row, remove the `.deferred` marker, and re-fire the download.

    3. Author src/snakemake/rules/m1_download.smk. Include `configfile: "config/pipeline.yaml"` (or use `include:` if already configured). Rule structure (one rule per source_tag using a wildcard expansion):

    ```python
    # src/snakemake/rules/m1_download.smk
    import pandas as pd, os
    MANIFEST = os.path.join(workflow.basedir, "../../config/download_manifest_m1_portal.tsv")
    _df = pd.read_csv(MANIFEST, sep="\t") if os.path.exists(MANIFEST) else pd.DataFrame()
    SOURCE_TAGS = _df["source_tag"].tolist() if not _df.empty else []

    rule m1_download_portal_row:
        output:
            flag = os.path.join(config["paths"]["raw_sumstats_v2"],
                                ".download_complete.{source_tag}")
        params:
            manifest = MANIFEST,
            tag = "{source_tag}"
        conda: "../../envs/m1-download.yml"
        resources:
            mem_mb=2000,
            runtime=2880,   # standard queue max per feedback_lsf_queues
        shell:
            "grep -P '^{params.tag}\\t' {params.manifest} | "
            "bash bin/download_sumstats_v2.sh --manifest-stdin && "
            "touch {output.flag}"

    rule m1_download_all:
        input:
            expand(os.path.join(config["paths"]["raw_sumstats_v2"],
                               ".download_complete.{t}"), t=SOURCE_TAGS),
    ```

    The `--manifest-stdin` flag is added in Task 1's bin/ edits so a single-row manifest can be piped in (implementation: `if [ "$1" == "--manifest-stdin" ]; then while IFS=$'\t' read -r tag url dir fname cookie sha t a c y; do fetch_one "$url" "$dir" "$fname"; done`).

    4. Author src/python/freeze_sha256_manifest.py:

    ```python
    #!/usr/bin/env python3
    """Deterministic SHA-256 manifest for a directory tree.

    Usage:
      python freeze_sha256_manifest.py --root data/raw/sumstats_v2 \
        --out data/raw/sumstats_v2/sha256_manifest.tsv --no-mtime
    Re-running MUST produce byte-identical TSV when --no-mtime is set
    (enables OSF paste verification).
    """
    import argparse, hashlib
    from pathlib import Path

    def sha256_of_file(p: Path) -> str:
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    def main():
        ap = argparse.ArgumentParser()
        ap.add_argument("--root", type=Path, required=True)
        ap.add_argument("--out",  type=Path, required=True)
        ap.add_argument("--no-mtime", action="store_true")
        ap.add_argument("--skip-glob", default="*.partial,*.deferred,.download_complete*")
        args = ap.parse_args()
        skips = set(args.skip_glob.split(","))
        files = []
        for p in sorted(args.root.rglob("*")):
            if not p.is_file(): continue
            if any(p.match(s) for s in skips): continue
            rel = p.relative_to(args.root).as_posix()
            files.append((rel, sha256_of_file(p), p.stat().st_size,
                          None if args.no_mtime else p.stat().st_mtime))
        cols = ["relative_path", "sha256", "bytes"]
        if not args.no_mtime: cols.append("mtime_unix")
        with open(args.out, "w") as fh:
            fh.write("\t".join(cols) + "\n")
            for row in files:
                fh.write("\t".join(str(x) for x in row if x is not None) + "\n")
        print(f"[freeze_sha256_manifest] wrote {len(files)} rows to {args.out}")

    if __name__ == "__main__":
        main()
    ```

    5. Author tests/m1/test_freeze_sha256_manifest.py with fixture: create 3-file tree in tmp_path, invoke main via subprocess, assert 3 rows; re-run; assert byte-identical; reorder with a hidden file and assert ignored.
  </action>
  <verify>
    <automated>bash bin/download_sumstats_v2.sh --help 2>&amp;1 | grep -q manifest &amp;&amp; test -f config/download_manifest_m1_portal.tsv &amp;&amp; awk -F'\t' 'NR>1 {print NF}' config/download_manifest_m1_portal.tsv | sort -u | wc -l | grep -q '^1$' &amp;&amp; test -f src/snakemake/rules/m1_download.smk &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_freeze_sha256_manifest.py -x 2>&amp;1 | tail -3 &amp;&amp; grep -r "/rs1/researchers\|/gpfs_common\|/share/clintonlab" src/snakemake/rules/m1_download.smk bin/download_sumstats_v2.sh config/download_manifest_m1_portal.tsv src/python/freeze_sha256_manifest.py | grep -v "^Binary" &amp;&amp; echo "FAIL: hardcoded path found" &amp;&amp; exit 1 || echo "path-parameterization OK"</automated>
  </verify>
  <done>Driver accepts --manifest flag + manifest-stdin; 17-row (or conditionally fewer) TSV manifest exists with consistent column count; Snakemake download rule loads without error; freeze_sha256_manifest.py passes its pytest; zero hardcoded absolute paths in any of the 4 files.</done>
</task>

<task id="m1-01-T2" type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Fire portal downloads + unzip Aragam + freeze raw SHA-256 manifest</name>
  <files>
    data/raw/sumstats_v2/GIANT2018/,
    data/raw/sumstats_v2/Loh2022/,
    data/raw/sumstats_v2/PAGE2019/,
    data/raw/sumstats_v2/DIAMANTE2022/,
    data/raw/sumstats_v2/GIGASTROKE2022/,
    data/raw/sumstats_v2/GBMI2022/,
    data/raw/sumstats_v2/MAGIC2021/,
    data/raw/sumstats_v2/Aragam2022/,
    data/raw/sumstats_v2/MVP2019/,
    data/raw/sumstats_v2/sha256_manifest.tsv,
    .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md
  </files>
  <read_first>
    - config/download_manifest_m1_portal.tsv (row list built in Task 1)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH.md (DIAMANTE cookie capture protocol — browser-side click-through)
    - data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt (from Wave 0; routes D-03 branch)
    - bin/download_sumstats_v2.sh (the extended driver from Task 1)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md (Wave 0 probe outcomes; update in-place with per-row landing status)
  </read_first>
  <what-built>Extended download driver + portal manifest + download.smk rule + sha256 freezer.</what-built>
  <how-to-verify>
    This is a human-gated execution checkpoint because (a) DIAMANTE requires Carter to capture the click-through cookie in a browser and export it as `DIAMANTE_COOKIE` env var for the shell session, and (b) several portal URLs (Broad, GIANT portal) may 403 and require Carter to manually open the browser URL to trigger the ToS acceptance before the curl retry succeeds.

    **Step 1: DIAMANTE cookie capture (~5 min Carter active).**
    Visit `https://diagram-consortium.org/downloads.html` in a browser, accept ToS, open DevTools → Application → Cookies, copy all DIAGRAM cookies into a single header string `name1=value1; name2=value2; ...`. Then on NCSU HPC shell: `export DIAMANTE_COOKIE="name1=value1; name2=value2; ..."`.

    **Step 2: Fire the batch download (~6-48 hrs wall depending on bandwidth).**
    Preferred path — Snakemake + LSF:
    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
      --snakefile workflow/Snakefile \
      --cluster "bash config/bsub_wrapper.sh -q standard -W 2880 -n 1 -M 2GB" \
      --jobs 5 \
      --use-conda \
      --printshellcmds \
      m1_download_all
    ```
    Alternative on login node for small files (bypass LSF):
    ```bash
    bash bin/download_sumstats_v2.sh --manifest config/download_manifest_m1_portal.tsv
    ```
    Monitor with `ls -lh data/raw/sumstats_v2/*/*/` and `bjobs`. If a portal URL returns HTTP 403/404, Carter either (a) opens the URL in a browser to trigger ToS acceptance + re-runs, (b) edits manifest row to switch to a Zenodo/NCBI mirror per feedback_url_rot_workarounds.md, or (c) marks the row DEFERRED in SUMSTATS-MANUAL-FETCH-STATUS.md with explicit reason.

    **Step 3: Unzip Aragam 2022 per D-03 branch from Wave 0.**
    ```bash
    cd data/raw/sumstats_v2/Aragam2022/
    unzip -o Aragam_2022_CARDIoGRAM_CAD_GWAS.zip
    ls -lh
    ```
    Branch (a) — AFR subset present: no further action; Wave 2 harmonize_aragam picks up the AFR file.
    Branch (b) — AFR absent: follow Wave 0 DEC-2026-04-24 disposition. Mark row 23 of SUMSTATS-UPGRADE.tsv with notes="D-03 branch b: Klarin 2018 MVP-AFR-CAD fallback (DOI 10.1038/s41591-018-0090-y, N~8.5k)". Wave 2 harmonize task routes to a one-off harmonize_klarin variant.

    **Step 4: Freeze primary raw SHA-256 manifest per D-13.**
    After every portal row is either landed OR marked DEFERRED:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python \
      src/python/freeze_sha256_manifest.py \
      --root data/raw/sumstats_v2 \
      --out data/raw/sumstats_v2/sha256_manifest.tsv \
      --no-mtime
    wc -l data/raw/sumstats_v2/sha256_manifest.tsv   # expect 27 (already landed) + N (this wave) + 1 header
    ```
    Verify determinism by running it twice; `diff` of the two outputs must be empty.

    Also copy the frozen manifest into the in-repo committed location so OSF paste survives (data/ is gitignored):
    ```bash
    cp data/raw/sumstats_v2/sha256_manifest.tsv \
       .planning/amendments/sha256_manifest_m1_frozen.tsv
    ```

    **Step 5: Update SUMSTATS-MANUAL-FETCH-STATUS.md with per-row landing outcomes.** Each row from config/download_manifest_m1_portal.tsv gets a status line: LANDED (bytes, sha) / DEFERRED (reason) / FAILED (reason, retry plan). Commit everything together: `feat(m1): portal sumstats landed + Aragam unzipped + raw SHA-256 manifest frozen (Wave 1 closeout)`.
  </how-to-verify>
  <resume-signal>Type "approved" after every manifest row is LANDED or explicitly DEFERRED, the sha256_manifest.tsv is frozen, and the Aragam D-03 branch disposition is reflected on disk. Or report which URL(s) blocked and for how long.</resume-signal>
</task>

</tasks>

<threat_model>
security_enforcement disabled — raw data fetch plan. Only concern is inadvertently committing DUA-covered data to git. Mitigation: `.gitignore` already excludes `data/`. The SUMSTATS-UPGRADE §8 rule to add explicit `data/raw/sumstats_v2/mvp_giri_bp_afr_2019/` exclusion only fires if D-06 DUA branch is ever taken (which D-06 explicitly rejects); skip unless disposition changes.
</threat_model>

<verification>
test -f config/download_manifest_m1_portal.tsv \
  && test -s bin/download_sumstats_v2.sh \
  && test -f src/snakemake/rules/m1_download.smk \
  && test -f src/python/freeze_sha256_manifest.py \
  && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_freeze_sha256_manifest.py -x \
  && test -f data/raw/sumstats_v2/sha256_manifest.tsv \
  && [ $(wc -l < data/raw/sumstats_v2/sha256_manifest.tsv) -ge 28 ] \
  && test -f .planning/amendments/sha256_manifest_m1_frozen.tsv \
  && ls data/raw/sumstats_v2/Aragam2022/*.tsv* 2>/dev/null || test -f data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt
</verification>

<success_criteria>
- `config/download_manifest_m1_portal.tsv` has 17 rows (minus Wave-0-driven deferrals) with consistent 10-column format
- `bin/download_sumstats_v2.sh` accepts `--manifest <path>` and `--manifest-stdin` flags without breaking the 27-row backward-compat manifest
- `src/snakemake/rules/m1_download.smk` loads in a Snakemake `--dry-run` and produces a DAG with one rule per source_tag
- `src/python/freeze_sha256_manifest.py` passes its pytest and produces byte-identical output across reruns with `--no-mtime`
- Every portal row in SUMSTATS-UPGRADE.tsv with status `to_download` is either landed on disk OR marked DEFERRED with explicit reason in SUMSTATS-MANUAL-FETCH-STATUS.md
- Aragam ZIP is unzipped; D-03 branch disposition is reflected in SUMSTATS-UPGRADE.tsv row 23 notes column
- `data/raw/sumstats_v2/sha256_manifest.tsv` has >= 27 (pre-existing) + landed-count + 1 header rows; deterministic across re-runs
- `.planning/amendments/sha256_manifest_m1_frozen.tsv` is the committed OSF-paste copy
- REQ-PUBLIC-DATA-ONLY holds: no dbGaP-covered data on disk; D-06 disposition documented
- REQ-PATH-PARAMETERIZATION holds: `grep -r "/rs1/researchers\|/gpfs_common" src/snakemake/rules/m1_download.smk bin/download_sumstats_v2.sh config/download_manifest_m1_portal.tsv` returns 0 matches
</success_criteria>

<output>
After completion, create `.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-01-SUMMARY.md` with:
- Per-source-tag row landing table: source_tag | status (LANDED/DEFERRED/FAILED) | bytes | sha256
- Aragam D-03 branch verdict (a or b) + file list
- DIAMANTE cookie capture outcome (worked / manual retry required)
- MAGIC FTP disposition (fired / deferred per Wave 0 egress probe)
- Giri 2019 MVP disposition (primary success / fallback to AoU queued)
- Raw SHA-256 manifest line count and commit hash of `.planning/amendments/sha256_manifest_m1_frozen.tsv`
- Total wall-clock time from first bsub to last landing
</output>
</content>
</invoke>