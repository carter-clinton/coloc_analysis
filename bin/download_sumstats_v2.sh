#!/bin/bash
# download_sumstats_v2.sh — fetch publicly-accessible sumstats per SUMSTATS-UPGRADE.tsv
#
# Scope: Track B genome-wide reframe, 12 traits × up to 7 ancestries (see
# .planning/amendments/SUMSTATS-UPGRADE.tsv for the authoritative map).
#
# This script covers the 19 directly-downloadable URLs (GLGC 2021 × 15 files,
# CKDGen 2019 × 2 files, Aragam 2022 × 1 zip). Portal-navigation sources
# (GIANT, GBMI, DIAMANTE, GIGASTROKE per-study, MAGIC, PAGE) and DUA-gated
# sources (MVP BP AFR) are documented in MANUAL_FETCH_REQUIRED.md alongside
# the destination directories.
#
# Destination: data/raw/sumstats_v2/{source}/{trait}/{ancestry}/{filename}
#
# Parallelism: xargs -P 5 per Carter's memory (saturate bandwidth).
# Retry: curl --retry 3 on transient failures.
# Idempotent: skip non-empty destinations.
#
# Usage:
#   nohup bash bin/download_sumstats_v2.sh > logs/sumstats_v2_$(date +%s).log 2>&1 &
#   disown

set -uo pipefail

ROOT="/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis"
cd "$ROOT"

DEST="data/raw/sumstats_v2"
LOG="logs/sumstats_v2_download_$(date +%Y%m%d_%H%M%S).log"
MANIFEST="$DEST/download_manifest.tsv"
FAIL_LOG="$DEST/failures.log"
mkdir -p "$DEST" logs

echo "[$(date +%Y-%m-%d\ %H:%M:%S)] download_sumstats_v2.sh starting. Log: $LOG" | tee -a "$LOG"

# -----------------------------------------------------------------------
# Build manifest: url<TAB>destdir<TAB>filename
# -----------------------------------------------------------------------

GLGC_TRANS="https://csg.sph.umich.edu/willer/public/glgc-lipids2021/results/trans_ancestry"
GLGC_ANC="https://csg.sph.umich.edu/willer/public/glgc-lipids2021/results/ancestry_specific"

cat > "$MANIFEST" <<'EOF'
https://personal.broadinstitute.org/ryank/Aragam_2022_CARDIoGRAM_CAD_GWAS.zip	data/raw/sumstats_v2/Aragam2022/CAD	Aragam_2022_CARDIoGRAM_CAD_GWAS.zip
https://ckdgen.imbi.uni-freiburg.de/files/Wuttke2019/20171016_MW_eGFR_overall_ALL_nstud61.dbgap.txt.gz	data/raw/sumstats_v2/CKDGen2019/eGFR/TRANS	20171016_MW_eGFR_overall_ALL_nstud61.dbgap.txt.gz
https://ckdgen.imbi.uni-freiburg.de/files/Wuttke2019/20171017_MW_eGFR_overall_EA_nstud42.dbgap.txt.gz	data/raw/sumstats_v2/CKDGen2019/eGFR/EUR	20171017_MW_eGFR_overall_EA_nstud42.dbgap.txt.gz
EOF

# GLGC trans-ancestry — verified 2026-04-23 against portal directory listing.
# Filename pattern: "with_BF_meta-analysis_AFR_EAS_EUR_HIS_SAS_{LDL,HDL,TC,logTG,nonHDL}_INV_ALL_with_N_1.gz"
# with_BF = with Bayes Factor; without_UKB variants also available (for UKB-leave-one-out validation)
GLGC_TRANS_PFX="with_BF_meta-analysis_AFR_EAS_EUR_HIS_SAS"
for trait in LDL HDL TC; do
  echo -e "${GLGC_TRANS}/${GLGC_TRANS_PFX}_${trait}_INV_ALL_with_N_1.gz\tdata/raw/sumstats_v2/GLGC2021/${trait}/TRANS\t${GLGC_TRANS_PFX}_${trait}_INV_ALL_with_N_1.gz" >> "$MANIFEST"
done
echo -e "${GLGC_TRANS}/${GLGC_TRANS_PFX}_logTG_INV_ALL_with_N_1.gz\tdata/raw/sumstats_v2/GLGC2021/TG/TRANS\t${GLGC_TRANS_PFX}_logTG_INV_ALL_with_N_1.gz" >> "$MANIFEST"

# GLGC ancestry-specific — verified 2026-04-23.
# Filename pattern differs by ancestry:
#   EUR/AFR/SAS: "{TRAIT}_INV_{ANC}_HRC_1KGP3_others_ALL.meta.singlevar.results.gz"
#   EAS/HIS:     "{TRAIT}_INV_{ANC}_1KGP3_ALL.meta.singlevar.results.gz"
for trait in LDL HDL TC; do
  for anc in EUR AFR SAS; do
    echo -e "${GLGC_ANC}/${trait}_INV_${anc}_HRC_1KGP3_others_ALL.meta.singlevar.results.gz\tdata/raw/sumstats_v2/GLGC2021/${trait}/${anc}\t${trait}_INV_${anc}_HRC_1KGP3_others_ALL.meta.singlevar.results.gz" >> "$MANIFEST"
  done
  for anc in EAS HIS; do
    echo -e "${GLGC_ANC}/${trait}_INV_${anc}_1KGP3_ALL.meta.singlevar.results.gz\tdata/raw/sumstats_v2/GLGC2021/${trait}/${anc}\t${trait}_INV_${anc}_1KGP3_ALL.meta.singlevar.results.gz" >> "$MANIFEST"
  done
done
# TG uses logTG prefix (same ancestry-pattern differentiation)
for anc in EUR AFR SAS; do
  echo -e "${GLGC_ANC}/logTG_INV_${anc}_HRC_1KGP3_others_ALL.meta.singlevar.results.gz\tdata/raw/sumstats_v2/GLGC2021/TG/${anc}\tlogTG_INV_${anc}_HRC_1KGP3_others_ALL.meta.singlevar.results.gz" >> "$MANIFEST"
done
for anc in EAS HIS; do
  echo -e "${GLGC_ANC}/logTG_INV_${anc}_1KGP3_ALL.meta.singlevar.results.gz\tdata/raw/sumstats_v2/GLGC2021/TG/${anc}\tlogTG_INV_${anc}_1KGP3_ALL.meta.singlevar.results.gz" >> "$MANIFEST"
done

wc -l "$MANIFEST"
echo "[$(date +%H:%M:%S)] Manifest assembled at $MANIFEST" | tee -a "$LOG"

# -----------------------------------------------------------------------
# fetch_one: download a single URL idempotently
# -----------------------------------------------------------------------

fetch_one() {
  local url="$1"
  local destdir="$2"
  local fname="$3"
  local dest="${destdir}/${fname}"
  local ts="[$(date +%H:%M:%S)]"

  mkdir -p "$destdir"

  if [ -f "$dest" ] && [ -s "$dest" ]; then
    echo "${ts} SKIP: $dest (exists, $(du -h "$dest" | cut -f1))"
    return 0
  fi

  echo "${ts} START: $url"
  if curl --fail --silent --show-error --location \
          --retry 3 --retry-delay 5 --retry-max-time 600 \
          --connect-timeout 30 --max-time 7200 \
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
# Parallelize: 5 concurrent downloads (Carter's parallel-downloads rule)
# -----------------------------------------------------------------------

echo "[$(date +%H:%M:%S)] Firing $(wc -l < "$MANIFEST") downloads at P=5" | tee -a "$LOG"

# shellcheck disable=SC2002
cat "$MANIFEST" | xargs -P 5 -n 3 -d '\n' bash -c '
  IFS=$'"'"'\t'"'"' read -r url destdir fname <<< "$1"
  fetch_one "$url" "$destdir" "$fname"
' _ 2>&1 | tee -a "$LOG"

# -----------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------

TOTAL=$(wc -l < "$MANIFEST")
DOWNLOADED=$(find "$DEST" -type f \( -name "*.gz" -o -name "*.zip" \) 2>/dev/null | wc -l)
FAILED=0
[ -f "$FAIL_LOG" ] && FAILED=$(wc -l < "$FAIL_LOG")

echo "" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)] Download pass complete." | tee -a "$LOG"
echo "  Manifest URLs:   $TOTAL" | tee -a "$LOG"
echo "  Files on disk:   $DOWNLOADED" | tee -a "$LOG"
echo "  Failures:        $FAILED (see $FAIL_LOG if >0)" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Next steps hint
echo "Next: verify checksums (none published; fall back to variant-count + MAF sanity checks)" | tee -a "$LOG"
echo "Next: unpack Aragam_2022_CARDIoGRAM_CAD_GWAS.zip for per-ancestry CAD files" | tee -a "$LOG"
echo "Next: manual-fetch sources per data/raw/sumstats_v2/MANUAL_FETCH_REQUIRED.md" | tee -a "$LOG"
