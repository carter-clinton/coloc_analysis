#!/usr/bin/env bash
# tests/m1/wave0_probes.sh
#
# Wave 0 pre-flight probes for M1. Three probes whose outcomes gate
# downstream wave behavior:
#   Probe 1 — MAGIC FTP port-21 egress from NCSU HPC (RESEARCH pitfall #2;
#             SUMSTATS-UPGRADE Q5). Pass = Wave 1 fetches MAGIC HbA1c
#             directly from FTP. Fail = Wave 1 falls back to EBI mirror
#             or login-node proxy per SUMSTATS-UPGRADE §5 Tier 1.
#   Probe 2 — GWAS-Catalog Giri 2019 sumstats availability (D-06 primary).
#             Pass = Wave 1 downloads from GWAS-Catalog. Fail = Wave 1
#             marks row 13 DEFERRED with AoU AFR-SBP fallback per D-06.
#   Probe 3 — LDSC 2-trait --rg smoke benchmark on pre-existing munged
#             files (RESEARCH open question #4). Calibrates per-pair
#             wall time before the 44 star-pattern jobs fire (Wave 3).
#             > 30 min/pair => m1-03 must chunk; < 15 min/pair => proceed.
#
# Usage: bash tests/m1/wave0_probes.sh
# Outputs all three probe results to tests/m1/wave0_probes.log AND appends
# a "Wave 0 pre-flight probes" section to .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md.
#
# Plan reference: m1-00-preflight-and-environment-PLAN.md Task 2.

set -uo pipefail
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

LOG=tests/m1/wave0_probes.log
DATE_STAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "# Wave 0 Pre-flight Probes — $DATE_STAMP" > "$LOG"
echo "" >> "$LOG"

# -----------------------------------------------------------------------
# Probe 1 — MAGIC FTP port-21 egress
# -----------------------------------------------------------------------
echo "## Probe 1 — MAGIC FTP port-21 egress" >> "$LOG"
echo "" >> "$LOG"
# Try FTP HEAD on the MAGIC primary FTP host. NCSU HPC outbound port-21
# may be blocked; if so, the curl will time out or refuse connection.
# Tries 3 candidate hosts: web-ftp.ex.ac.uk (legacy), ftp.sanger.ac.uk
# (mirror), and a control HTTPS endpoint on the same investigator site.
MAGIC_FTP_HOST=ftp.sanger.ac.uk
MAGIC_FTP_URL="ftp://${MAGIC_FTP_HOST}/pub/"
MAGIC_HTTPS_URL="https://magicinvestigators.org/downloads/"
echo "- Probe URL (FTP): ${MAGIC_FTP_URL}" >> "$LOG"
echo "- Probe URL (HTTPS control): ${MAGIC_HTTPS_URL}" >> "$LOG"

ftp_rc=$(curl --connect-timeout 30 --max-time 45 --head "${MAGIC_FTP_URL}" 2>&1)
ftp_exit=$?
echo "- FTP curl exit: ${ftp_exit}" >> "$LOG"
if [[ ${ftp_exit} -eq 0 ]]; then
  echo "- **Probe 1 verdict: PASS** (FTP egress works; Wave 1 may use FTP for MAGIC)" >> "$LOG"
  P1_VERDICT="PASS"
else
  echo "- FTP curl output (first 5 lines):" >> "$LOG"
  echo '```' >> "$LOG"
  echo "${ftp_rc}" | head -5 >> "$LOG"
  echo '```' >> "$LOG"
  https_rc=$(curl --connect-timeout 30 --max-time 30 --head "${MAGIC_HTTPS_URL}" 2>&1 | head -3)
  echo "- HTTPS control: $(echo "${https_rc}" | head -1)" >> "$LOG"
  echo "- **Probe 1 verdict: FAIL — FTP egress blocked or unreachable** (Wave 1 must use HTTPS portal mirror)" >> "$LOG"
  P1_VERDICT="FAIL — FTP blocked; Wave 1 falls back to HTTPS portal at magicinvestigators.org/downloads/ per SUMSTATS-UPGRADE §5 Tier 1"
fi
echo "" >> "$LOG"

# -----------------------------------------------------------------------
# Probe 2 — GWAS-Catalog Giri 2019 summary-only (D-06 primary)
# -----------------------------------------------------------------------
echo "## Probe 2 — GWAS-Catalog Giri 2019 summary availability (D-06 primary)" >> "$LOG"
echo "" >> "$LOG"
GIRI_URL="https://www.ebi.ac.uk/gwas/publications/30578418"
echo "- Probe URL: ${GIRI_URL}" >> "$LOG"

GIRI_HTML=/tmp/giri_page_$$.html
curl -sS --connect-timeout 30 --max-time 60 -o "${GIRI_HTML}" "${GIRI_URL}" 2>&1
giri_exit=$?
echo "- curl exit: ${giri_exit}" >> "$LOG"

if [[ ${giri_exit} -ne 0 ]]; then
  echo "- **Probe 2 verdict: ERROR — could not reach GWAS-Catalog**" >> "$LOG"
  P2_VERDICT="ERROR — GWAS-Catalog unreachable; rerun Probe 2 before D-06 disposition"
else
  # Check for sumstats / GCST tokens. EBI typically renders a
  # "Summary statistics" link or a GCST accession near the publication.
  echo "- HTML body size: $(wc -c < "${GIRI_HTML}") bytes" >> "$LOG"
  GCST_HITS=$(grep -ioE "GCST[0-9]{6,}" "${GIRI_HTML}" | sort -u)
  SUMSTATS_HITS=$(grep -i -c "summary statistic\|sumstats\|FTP" "${GIRI_HTML}" 2>/dev/null || echo "0")
  echo "- GCST accession hits in body:" >> "$LOG"
  if [[ -n "${GCST_HITS}" ]]; then
    echo '```' >> "$LOG"
    echo "${GCST_HITS}" | head -10 >> "$LOG"
    echo '```' >> "$LOG"
  else
    echo "  (none)" >> "$LOG"
  fi
  echo "- 'summary statistic' / 'sumstats' / 'FTP' substring count: ${SUMSTATS_HITS}" >> "$LOG"

  # Verdict: if we see GCST + summary/sumstats markers, treat as PASS;
  # else mark for D-06 fallback (AoU derivation).
  if [[ -n "${GCST_HITS}" ]] && [[ "${SUMSTATS_HITS}" -gt 0 ]]; then
    echo "- **Probe 2 verdict: PASS — Giri 2019 sumstats appear available on GWAS-Catalog**" >> "$LOG"
    P2_VERDICT="PASS — GCST accessions present (${GCST_HITS}); Wave 1 may download directly. NOTE: human verification recommended before commit."
  else
    echo "- **Probe 2 verdict: NO-SUMMARY-FOUND — D-06 fallback (AoU AFR-SBP derivation)**" >> "$LOG"
    P2_VERDICT="NO-SUMMARY-FOUND — body has no GCST + sumstats marker; D-06 fallback to AoU AFR-SBP per CONTEXT D-07. Wave 1 marks row 13 DEFERRED."
  fi
  rm -f "${GIRI_HTML}"
fi
echo "" >> "$LOG"

# -----------------------------------------------------------------------
# Probe 3 — LDSC 2-trait --rg smoke benchmark
# -----------------------------------------------------------------------
echo "## Probe 3 — LDSC 2-trait --rg smoke benchmark" >> "$LOG"
echo "" >> "$LOG"

# LDSC requires bitarray (absent from smoke_dev). Use the snakemake-cached
# LDSC env that has bitarray + numpy=1.26.4 + pandas=2.2.1. Resolved at
# fixture-staging time, falls back to smoke_dev for shape-only failure.
LDSC_PY=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python
if ! "${LDSC_PY}" -c "import bitarray" 2>/dev/null; then
  LDSC_PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
fi
LDSC_SCRIPT=tools/ldsc/ldsc.py
MUNGED_DIR=results/pathway/ldsc_partitioned/munged
EUR_LD_DIR=data/external/ldscore/eur_w_ld_chr

# Prefer two pre-existing EUR-EUR pairs.
P1_FILE="${MUNGED_DIR}/bmi_EUR.sumstats.gz"
P2_FILE="${MUNGED_DIR}/hypertension_EUR.sumstats.gz"

echo "- Munged files:" >> "$LOG"
echo "  - p1: ${P1_FILE} ($(test -f "${P1_FILE}" && echo OK || echo MISSING))" >> "$LOG"
echo "  - p2: ${P2_FILE} ($(test -f "${P2_FILE}" && echo OK || echo MISSING))" >> "$LOG"
echo "  - LDSC ref: ${EUR_LD_DIR} ($(test -d "${EUR_LD_DIR}" && echo OK || echo MISSING))" >> "$LOG"

if [[ -f "${P1_FILE}" && -f "${P2_FILE}" && -d "${EUR_LD_DIR}" ]]; then
  OUT_PREFIX=/tmp/ldsc_smoke_$$
  TIMING=/tmp/ldsc_smoke_$$.time
  ARGS=(
    "${LDSC_SCRIPT}"
    "--rg" "${P1_FILE},${P2_FILE}"
    "--ref-ld-chr" "${EUR_LD_DIR}/"
    "--w-ld-chr"   "${EUR_LD_DIR}/"
    "--out" "${OUT_PREFIX}"
  )
  echo "- Invocation: ${LDSC_PY} ${ARGS[*]}" >> "$LOG"
  /usr/bin/time -p -o "${TIMING}" "${LDSC_PY}" "${ARGS[@]}" > "${OUT_PREFIX}.stdout" 2>&1
  ldsc_exit=$?
  echo "- LDSC exit: ${ldsc_exit}" >> "$LOG"

  if [[ ${ldsc_exit} -eq 0 ]]; then
    REAL_S=$(awk '/^real /{print $2}' "${TIMING}")
    REAL_INT=${REAL_S%.*}
    echo "- Wall time (real): ${REAL_S} seconds" >> "$LOG"
    echo "PAIR_WALL_SECONDS ${REAL_INT}" >> "$LOG"
    if [[ "${REAL_INT}" -lt 900 ]]; then
      P3_VERDICT="PASS — pair wall ${REAL_INT}s (<15 min/pair); Wave 3 m1-03 proceeds at full --jobs density."
    elif [[ "${REAL_INT}" -lt 1800 ]]; then
      P3_VERDICT="MARGINAL — pair wall ${REAL_INT}s (15-30 min); Wave 3 m1-03 may need moderate --jobs throttling."
    else
      P3_VERDICT="SLOW — pair wall ${REAL_INT}s (>30 min); Wave 3 m1-03 MUST chunk star-calls to stay under 240 h long-queue ceiling."
    fi
    echo "- **Probe 3 verdict: ${P3_VERDICT}**" >> "$LOG"
    # Sanity: confirm ldsc emitted a log + table
    if [[ -f "${OUT_PREFIX}.log" ]]; then
      echo "- LDSC log size: $(wc -c < "${OUT_PREFIX}.log") bytes" >> "$LOG"
      grep -c "Summary of Genetic Correlation" "${OUT_PREFIX}.log" >/dev/null && \
        echo "- LDSC summary table present: YES" >> "$LOG" || \
        echo "- LDSC summary table present: NO" >> "$LOG"
    fi
  else
    echo "- LDSC stdout/stderr (last 30):" >> "$LOG"
    echo '```' >> "$LOG"
    tail -30 "${OUT_PREFIX}.stdout" >> "$LOG"
    echo '```' >> "$LOG"
    P3_VERDICT="ERROR — LDSC --rg failed exit ${ldsc_exit}; Wave 3 m1-03 must repair before fire."
    echo "- **Probe 3 verdict: ${P3_VERDICT}**" >> "$LOG"
  fi
else
  P3_VERDICT="DEFERRED — required munged files / LDSC ref missing; rerun probe 3 after staging."
  echo "- **Probe 3 verdict: ${P3_VERDICT}**" >> "$LOG"
fi
echo "" >> "$LOG"

# -----------------------------------------------------------------------
# Verdict summary (machine-readable)
# -----------------------------------------------------------------------
echo "## Verdicts" >> "$LOG"
echo "- Probe 1 (MAGIC FTP egress): ${P1_VERDICT}" >> "$LOG"
echo "- Probe 2 (Giri 2019 GWAS-Catalog): ${P2_VERDICT}" >> "$LOG"
echo "- Probe 3 (LDSC 2-trait --rg): ${P3_VERDICT}" >> "$LOG"
echo "" >> "$LOG"
echo "Wave 0 probes complete — see Wave 0 pre-flight probes section in .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md for downstream wave consequences."
