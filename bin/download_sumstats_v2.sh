#!/bin/bash
# download_sumstats_v2.sh — fetch publicly-accessible sumstats per SUMSTATS-UPGRADE.tsv
#
# Scope: Track B genome-wide reframe, 12 traits × up to 7 ancestries (see
# .planning/amendments/SUMSTATS-UPGRADE.tsv for the authoritative map).
#
# Original mode (no flags): fires the inline 27-row manifest covering GLGC 2021,
# CKDGen 2019 and the Aragam 2022 ZIP (proven 2026-04-22 → 2026-04-23, 40.4 GB
# landed). Idempotent — re-runs skip non-empty destinations.
#
# Wave 1 mode: pass `--manifest <tsv>` to read a 10-column TSV (header row +
# data rows) at:
#   source_tag	url	target_dir	filename	requires_cookie_env	sha256_expected	trait	ancestry	consortium	year
# DIAMANTE rows opt into a `-b "$DIAMANTE_COOKIE"` curl augment via the
# `requires_cookie_env=DIAMANTE_COOKIE` column. If env var unset, driver emits
# "MANUAL ACTION REQUIRED" and `return 0` for that row (does NOT fail the batch).
# `PENDING_*` URLs (Loh 2022 D-01 accession-pending) skip-with-marker (.deferred)
# rather than fail.
#
# Stdin mode: pass `--manifest-stdin` to feed a single (header-less) TSV row on
# stdin — used by the Snakemake per-source-tag wrapper rule.
#
# Destination: data/raw/sumstats_v2/{source}/{trait}/{ancestry}/{filename}
#
# Parallelism: xargs -P 5 per Carter's memory (saturate bandwidth).
# Retry: curl --retry 3 on transient failures.
# Idempotent: skip non-empty destinations.
#
# Usage:
#   # Original 27-row driver:
#   nohup bash bin/download_sumstats_v2.sh > logs/sumstats_v2_$(date +%s).log 2>&1 &
#   disown
#
#   # Wave 1 portal manifest:
#   bash bin/download_sumstats_v2.sh --manifest config/download_manifest_m1_portal.tsv
#
#   # Single-row from stdin (Snakemake wrapper):
#   grep -P '^GLGC2021\t' config/download_manifest_m1_portal.tsv | \
#     bash bin/download_sumstats_v2.sh --manifest-stdin

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DEST="data/raw/sumstats_v2"
LOG="logs/sumstats_v2_download_$(date +%Y%m%d_%H%M%S).log"
FAIL_LOG="$DEST/failures.log"
mkdir -p "$DEST" logs

# -----------------------------------------------------------------------
# fetch_one: download a single URL idempotently
#   fetch_one <url> <destdir> <filename> [<cookie_env_name>] [<source_tag>]
# Backwards-compatible: callers from the inline 27-row mode still pass 3 args.
# -----------------------------------------------------------------------

fetch_one() {
  local url="$1"
  local destdir="$2"
  local fname="$3"
  local cookie_env_name="${4:-NONE}"   # "DIAMANTE_COOKIE" | "NONE" | ""
  local source_tag="${5:-}"
  local dest="${destdir}/${fname}"
  local ts="[$(date +%H:%M:%S)]"

  # Sentinel handling: PENDING_* URLs (e.g. Loh 2022 D-01 accession unresolved)
  # touch a .deferred placeholder rather than fail the batch.
  if [[ "$url" == PENDING_* ]]; then
    mkdir -p "$destdir"
    touch "${destdir}/.deferred"
    echo "${ts} DEFERRED: ${source_tag:-?} url=${url} (placeholder written at ${destdir}/.deferred)"
    return 0
  fi

  mkdir -p "$destdir"

  if [ -f "$dest" ] && [ -s "$dest" ]; then
    echo "${ts} SKIP:  $dest (exists, $(du -h "$dest" 2>/dev/null | cut -f1))"
    return 0
  fi

  # Cookie augmentation. If a row declares requires_cookie_env=DIAMANTE_COOKIE
  # but the env var is unset, emit MANUAL ACTION and return 0 (does not fail
  # the batch — Carter captures the cookie out-of-band and re-fires).
  local curl_cookie_arg=()
  if [[ "$cookie_env_name" != "NONE" && -n "$cookie_env_name" ]]; then
    local cookie_value="${!cookie_env_name:-}"
    if [[ -z "$cookie_value" ]]; then
      echo "${ts} MANUAL ACTION REQUIRED: $cookie_env_name unset; ${source_tag:-?} skipped."
      echo "    -> capture cookie from ${url%%/downloads*}/downloads.html in browser DevTools,"
      echo "       export ${cookie_env_name}=\"name1=value1; name2=value2\", then re-fire."
      return 0
    fi
    curl_cookie_arg=(-b "$cookie_value")
  fi

  echo "${ts} START: $url"
  if curl --fail --silent --show-error --location \
          --retry 3 --retry-delay 5 --retry-max-time 600 \
          --connect-timeout 30 --max-time 7200 \
          "${curl_cookie_arg[@]}" \
          --output "$dest" \
          "$url"; then
    local sz
    sz="$(du -h "$dest" 2>/dev/null | cut -f1)"
    echo "${ts} OK:    $sz $dest"
  else
    local rc=$?
    echo "${ts} FAIL:  $url (curl rc=$rc) -> $dest"
    rm -f "$dest"
    echo -e "${url}\t${destdir}\t${fname}\trc=${rc}" >> "$FAIL_LOG"
    return 1
  fi
}
export -f fetch_one

# -----------------------------------------------------------------------
# Mode dispatch: --manifest <path> | --manifest-stdin | (default = inline 27-row)
# -----------------------------------------------------------------------

usage() {
  cat <<'USAGE'
Usage: download_sumstats_v2.sh [--manifest <tsv> | --manifest-stdin | --help]

Modes:
  (no flag)             Fire the inline 27-row backward-compat manifest
                        (GLGC 2021 + CKDGen 2019 + Aragam 2022 ZIP).
  --manifest <tsv>      Read 10-column TSV (header skipped):
                        source_tag url target_dir filename requires_cookie_env
                        sha256_expected trait ancestry consortium year
  --manifest-stdin      Same column schema, single row on stdin (no header).
  --help                Print this message.

Cookie env vars (optional):
  DIAMANTE_COOKIE       Cookie header string for diagram-consortium.org rows
                        whose requires_cookie_env column is "DIAMANTE_COOKIE".
                        If unset on such a row: row skipped with MANUAL ACTION
                        message; batch continues (does NOT fail).

Sentinel URLs:
  PENDING_*             Skip-with-marker; .deferred placeholder written in target_dir.
USAGE
}

run_inline_27_row_manifest() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] download_sumstats_v2.sh starting (inline mode). Log: $LOG" | tee -a "$LOG"
  local MANIFEST="$DEST/download_manifest.tsv"

  GLGC_TRANS="https://csg.sph.umich.edu/willer/public/glgc-lipids2021/results/trans_ancestry"
  GLGC_ANC="https://csg.sph.umich.edu/willer/public/glgc-lipids2021/results/ancestry_specific"

  cat > "$MANIFEST" <<'EOF'
https://personal.broadinstitute.org/ryank/Aragam_2022_CARDIoGRAM_CAD_GWAS.zip	data/raw/sumstats_v2/Aragam2022/CAD	Aragam_2022_CARDIoGRAM_CAD_GWAS.zip
https://ckdgen.imbi.uni-freiburg.de/files/Wuttke2019/20171016_MW_eGFR_overall_ALL_nstud61.dbgap.txt.gz	data/raw/sumstats_v2/CKDGen2019/eGFR/TRANS	20171016_MW_eGFR_overall_ALL_nstud61.dbgap.txt.gz
https://ckdgen.imbi.uni-freiburg.de/files/Wuttke2019/20171017_MW_eGFR_overall_EA_nstud42.dbgap.txt.gz	data/raw/sumstats_v2/CKDGen2019/eGFR/EUR	20171017_MW_eGFR_overall_EA_nstud42.dbgap.txt.gz
EOF

  GLGC_TRANS_PFX="with_BF_meta-analysis_AFR_EAS_EUR_HIS_SAS"
  for trait in LDL HDL TC; do
    echo -e "${GLGC_TRANS}/${GLGC_TRANS_PFX}_${trait}_INV_ALL_with_N_1.gz\tdata/raw/sumstats_v2/GLGC2021/${trait}/TRANS\t${GLGC_TRANS_PFX}_${trait}_INV_ALL_with_N_1.gz" >> "$MANIFEST"
  done
  echo -e "${GLGC_TRANS}/${GLGC_TRANS_PFX}_logTG_INV_ALL_with_N_1.gz\tdata/raw/sumstats_v2/GLGC2021/TG/TRANS\t${GLGC_TRANS_PFX}_logTG_INV_ALL_with_N_1.gz" >> "$MANIFEST"

  for trait in LDL HDL TC; do
    for anc in EUR AFR SAS; do
      echo -e "${GLGC_ANC}/${trait}_INV_${anc}_HRC_1KGP3_others_ALL.meta.singlevar.results.gz\tdata/raw/sumstats_v2/GLGC2021/${trait}/${anc}\t${trait}_INV_${anc}_HRC_1KGP3_others_ALL.meta.singlevar.results.gz" >> "$MANIFEST"
    done
    for anc in EAS HIS; do
      echo -e "${GLGC_ANC}/${trait}_INV_${anc}_1KGP3_ALL.meta.singlevar.results.gz\tdata/raw/sumstats_v2/GLGC2021/${trait}/${anc}\t${trait}_INV_${anc}_1KGP3_ALL.meta.singlevar.results.gz" >> "$MANIFEST"
    done
  done
  for anc in EUR AFR SAS; do
    echo -e "${GLGC_ANC}/logTG_INV_${anc}_HRC_1KGP3_others_ALL.meta.singlevar.results.gz\tdata/raw/sumstats_v2/GLGC2021/TG/${anc}\tlogTG_INV_${anc}_HRC_1KGP3_others_ALL.meta.singlevar.results.gz" >> "$MANIFEST"
  done
  for anc in EAS HIS; do
    echo -e "${GLGC_ANC}/logTG_INV_${anc}_1KGP3_ALL.meta.singlevar.results.gz\tdata/raw/sumstats_v2/GLGC2021/TG/${anc}\tlogTG_INV_${anc}_1KGP3_ALL.meta.singlevar.results.gz" >> "$MANIFEST"
  done

  wc -l "$MANIFEST"
  echo "[$(date +%H:%M:%S)] Manifest assembled at $MANIFEST" | tee -a "$LOG"
  echo "[$(date +%H:%M:%S)] Firing $(wc -l < "$MANIFEST") downloads at P=5" | tee -a "$LOG"

  cat "$MANIFEST" | xargs -P 5 -n 1 -d '\n' bash -c '
    IFS=$'"'"'\t'"'"' read -r url destdir fname <<< "$1"
    fetch_one "$url" "$destdir" "$fname"
  ' _ 2>&1 | tee -a "$LOG"
}

# Read a 10-column manifest TSV (header skipped) and dispatch fetch_one rows
# in parallel via xargs -P 5. Each row carries (source_tag, url, target_dir,
# filename, requires_cookie_env, ...).
run_manifest_file() {
  local manifest_path="$1"
  if [[ ! -f "$manifest_path" ]]; then
    echo "ERROR: manifest path not found: $manifest_path" >&2
    return 1
  fi
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] download_sumstats_v2.sh manifest mode: $manifest_path" | tee -a "$LOG"
  local nrows
  nrows=$(awk 'NR>1 && NF>=4' "$manifest_path" | wc -l)
  echo "[$(date +%H:%M:%S)] Firing $nrows manifest rows at P=5" | tee -a "$LOG"

  # Skip header row (NR>1). Strip trailing CR if present (Windows-edited TSVs).
  awk 'NR>1 && NF>=4 {sub(/\r$/, ""); print}' "$manifest_path" | \
    xargs -P 5 -n 1 -d '\n' bash -c '
      IFS=$'"'"'\t'"'"' read -r tag url dir fname cookie_env sha trait anc consortium year <<< "$1"
      fetch_one "$url" "$dir" "$fname" "${cookie_env:-NONE}" "$tag"
    ' _ 2>&1 | tee -a "$LOG"
}

# Read a single manifest row (no header) from stdin and process it inline.
# Used by the Snakemake per-source-tag wrapper rule.
run_manifest_stdin() {
  local line
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    line="${line%$'\r'}"
    IFS=$'\t' read -r tag url dir fname cookie_env sha trait anc consortium year <<< "$line"
    fetch_one "$url" "$dir" "$fname" "${cookie_env:-NONE}" "$tag"
  done
}

# -----------------------------------------------------------------------
# Argument dispatch
# -----------------------------------------------------------------------

if [[ $# -eq 0 ]]; then
  run_inline_27_row_manifest
else
  case "${1:-}" in
    --help|-h)
      usage
      exit 0
      ;;
    --manifest)
      if [[ -z "${2:-}" ]]; then
        echo "ERROR: --manifest requires a path argument" >&2
        usage
        exit 2
      fi
      run_manifest_file "$2"
      ;;
    --manifest-stdin)
      run_manifest_stdin
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
fi

# -----------------------------------------------------------------------
# Summary (always)
# -----------------------------------------------------------------------

TOTAL=$(find "$DEST" -type f \( -name "*.gz" -o -name "*.zip" -o -name "*.tsv" -o -name "*.txt" \) 2>/dev/null | wc -l)
FAILED=0
[ -f "$FAIL_LOG" ] && FAILED=$(wc -l < "$FAIL_LOG")

echo "" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)] download_sumstats_v2.sh pass complete." | tee -a "$LOG"
echo "  Files on disk under $DEST: $TOTAL" | tee -a "$LOG"
echo "  Failures (see $FAIL_LOG):  $FAILED" | tee -a "$LOG"
