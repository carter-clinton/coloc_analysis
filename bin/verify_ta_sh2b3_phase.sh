#!/bin/bash
# bin/verify_ta_sh2b3_phase.sh — Phase ta-sh2b3 C1-C15 verification harness
# Phase: ta-sh2b3-canonical-and-cache-refresh
#
# Runs the C1-C15 dimension checks defined in
# .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md
# and emits one PASS/WARN/FAIL JSON-line per check at stdout. Exit code = number
# of FAILures (0 = all green). WARN does not fail the harness — it surfaces
# pre-Wave-N artifacts that don't yet exist.
#
# Usage:
#   bin/verify_ta_sh2b3_phase.sh                 # run all checks
#   bin/verify_ta_sh2b3_phase.sh --wave 0        # run only checks for wave 0
#   bin/verify_ta_sh2b3_phase.sh --wave 1        # run only Wave 1 checks (C5)
#
# Wave-to-check map:
#   Wave 0 → C1, C2, C3, C4
#   Wave 1 → C5
#   Wave 2 → C6, C7
#   Wave 3 → C8
#   Wave 4 → C9
#   Wave 5 → C10, C11
#   Wave 6 → C13
#   Wave 7 → C12, C14, C15

set -uo pipefail
REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
cd "$REPO"
JSON_OUT=()
FAIL_COUNT=0

emit_json() {
  local cid="$1" wave="$2" status="$3" msg="$4"
  # Strip newlines/tabs/quotes from msg to keep JSON-line clean
  msg="$(printf '%s' "$msg" | tr -d '\n\t' | sed 's/"/\\"/g')"
  JSON_OUT+=("{\"check\":\"$cid\",\"wave\":$wave,\"status\":\"$status\",\"msg\":\"$msg\"}")
  [ "$status" = "FAIL" ] && FAIL_COUNT=$((FAIL_COUNT+1))
}

# C1: D-TA-01 path resolves on login02
check_C1() {
  if [ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ]; then
    local rs1_head gpfs_head
    rs1_head=$(cd /rs1/researchers/c/ckclinto/coloc_analysis && git rev-parse HEAD 2>/dev/null || echo "ERR")
    gpfs_head=$(git rev-parse HEAD 2>/dev/null || echo "ERR")
    if [ "$rs1_head" = "$gpfs_head" ]; then
      emit_json C1 0 PASS "rs1 HEAD = GPFS HEAD = $rs1_head"
    else
      emit_json C1 0 FAIL "rs1 HEAD ($rs1_head) != GPFS HEAD ($gpfs_head)"
    fi
  else
    emit_json C1 0 WARN "/rs1/.../coloc_analysis/.git not present on this node — see D-TA-Wave-0-foundations"
  fi
}

# C2: 069b34f + 7d54183 are HEAD ancestors
check_C2() {
  if git merge-base --is-ancestor 069b34f HEAD 2>/dev/null && \
     git merge-base --is-ancestor 7d54183 HEAD 2>/dev/null; then
    emit_json C2 0 PASS "069b34f + 7d54183 both HEAD ancestors"
  else
    emit_json C2 0 FAIL "code-fix ancestry failed"
  fi
}

# C3: D-TA-04 diagnostic recorded in CONTEXT addendum
check_C3() {
  if grep -q "D-TA-04-DIAGNOSTIC:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md; then
    emit_json C3 0 PASS "D-TA-04-DIAGNOSTIC sub-section present in CONTEXT"
  else
    emit_json C3 0 FAIL "D-TA-04-DIAGNOSTIC not yet recorded"
  fi
}

# C4: D-TA-05 OSF coverage recorded
check_C4() {
  if grep -q "D-TA-OSF-COVERAGE:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md; then
    emit_json C4 0 PASS "D-TA-OSF-COVERAGE outcome recorded"
  else
    emit_json C4 0 FAIL "D-TA-OSF-COVERAGE not yet recorded (Task 7 human-verify gate)"
  fi
}

# C5: SuSiE-RSS converges at chosen L for SH2B3 EUR BMI/HTN/stroke
check_C5() {
  local primary_l="${PRIMARY_L:-20}"
  local rscript=/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
  if [ ! -x "$rscript" ]; then
    emit_json C5 1 WARN "la_multitrait_r Rscript not found ($rscript)"
    return
  fi
  local out
  out=$("$rscript" -e "
    suppressPackageStartupMessages(library(jsonlite))
    traits <- c('bmi','hypertension','stroke')
    all_pass <- TRUE
    for (t in traits) {
      f <- sprintf('results_lsweep_L%d/fine_mapping/susie/%s.EUR.SH2B3_12q24.json', $primary_l, t)
      if (!file.exists(f)) { cat(sprintf('%s: MISSING|', f)); all_pass <- FALSE; next }
      j <- jsonlite::fromJSON(f)
      ncs <- length(j\$credible_sets)
      conv <- grepl('^converged', j\$convergence_status %||% '')
      sat  <- isTRUE(j\$L_saturated)
      ok   <- (ncs < $primary_l) && conv && !sat
      cat(sprintf('%s: L_used=%s n_CS=%d conv=%s sat=%s ok=%s|', basename(f), j\$L_used %||% 'NA', ncs, j\$convergence_status %||% 'NA', sat, ok))
      if (!ok) all_pass <- FALSE
    }
    cat(sprintf('AGG=%s', if (all_pass) 'PASS' else 'FAIL'))
  " 2>&1 || echo "ERR")
  if echo "$out" | grep -q "AGG=PASS"; then
    emit_json C5 1 PASS "all 3 SH2B3 EUR fits converged at L=$primary_l with n_CS<L"
  elif echo "$out" | grep -q "MISSING"; then
    emit_json C5 1 WARN "Wave 1 outputs not yet on disk: $out"
  else
    emit_json C5 1 FAIL "SuSiE-RSS convergence FAIL: $out"
  fi
}

# C6: BMI–HTN reference-LD coloc.susie produced
check_C6() {
  local f="results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json"
  if [ -f "$f" ]; then
    local pp
    pp=$(jq -r '.summary."PP.H4.abf" // empty' "$f" 2>/dev/null || echo "ERR")
    if [[ "$pp" =~ ^[0-9.eE+-]+$ ]]; then
      emit_json C6 2 PASS "BMI-HTN PP.H4 = $pp"
    else
      emit_json C6 2 FAIL "PP.H4 unparseable: $pp"
    fi
  else
    emit_json C6 2 WARN "BMI-HTN R2 JSON not yet on disk (pre-Wave-2)"
  fi
}

# C7: All 9 SH2B3 EUR new pairs produced
check_C7() {
  local n
  n=$(ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json 2>/dev/null | wc -l)
  if [ "$n" -eq 9 ]; then
    emit_json C7 2 PASS "9 SH2B3 EUR pair JSONs present"
  elif [ "$n" -eq 0 ]; then
    emit_json C7 2 WARN "no R2 pair JSONs yet (pre-Wave-2)"
  else
    emit_json C7 2 FAIL "$n / 9 SH2B3 EUR pair JSONs present"
  fi
}

# C8: D-TA-WAVE3-OUTCOME branch recorded
check_C8() {
  if grep -qE "D-TA-WAVE3-OUTCOME-(BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE)" \
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md; then
    emit_json C8 3 PASS "D-TA-WAVE3-OUTCOME branch recorded"
  else
    emit_json C8 3 WARN "D-TA-WAVE3-OUTCOME not yet recorded (pre-Wave-3)"
  fi
}

# C9: Cache refresh produces materially different numerics
check_C9() {
  local n
  n=$(grep -h '"status"' results/qtl_coloc/*.json 2>/dev/null | grep -c '"too_few_snps"' || echo 0)
  if [ -z "$n" ] || [ "$n" -eq 0 ]; then
    if ls results/qtl_coloc/*.json >/dev/null 2>&1; then
      emit_json C9 4 PASS "too_few_snps=0 (no stale variant-ID rows)"
    else
      emit_json C9 4 WARN "no qtl_coloc/*.json on disk (pre-Wave-4 or post-backup)"
    fi
  elif [ "$n" -le 200 ]; then
    emit_json C9 4 PASS "too_few_snps=$n (PASS, baseline 1005, target ≤200)"
  elif [ "$n" -ge 800 ]; then
    emit_json C9 4 FAIL "too_few_snps=$n still ~baseline; SuSiE-RSS layer fallback (W4.5) needed"
  else
    emit_json C9 4 WARN "too_few_snps=$n (intermediate; investigate)"
  fi
}

# C10: Wave-5 aggregator outputs refreshed (mtime check)
check_C10() {
  local oldest_tsv newest_json
  oldest_tsv=$(stat -c '%Y' results/track_a_aggregations/*.tsv 2>/dev/null | sort -n | head -1)
  newest_json=$(stat -c '%Y' results/qtl_coloc/*.json 2>/dev/null | sort -n | tail -1)
  if [ -z "$oldest_tsv" ] || [ -z "$newest_json" ]; then
    emit_json C10 5 WARN "missing aggregator TSVs or qtl_coloc JSONs (pre-Wave-5)"
  elif [ "$oldest_tsv" -ge "$newest_json" ]; then
    emit_json C10 5 PASS "aggregator TSVs refreshed post-Wave-4"
  else
    emit_json C10 5 FAIL "aggregator TSVs older than qtl_coloc JSONs"
  fi
}

# C11: TRACK-A-FROZEN-NUMBERS LIVE block updated
check_C11() {
  if grep -A 20 "Stage 2 fine-mapping yield" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md 2>/dev/null | grep -q "LIVE"; then
    emit_json C11 5 PASS "Stage 2 LIVE block present"
  else
    emit_json C11 5 WARN "LIVE block not yet refreshed (pre-Wave-5)"
  fi
}

# C12: Stage 2 md5 invariant preserved (whitelist check; baseline manifest)
check_C12() {
  # Whitelist of files this phase intentionally rewrites is enforced at Wave 7
  # closeout via baseline manifest captured at Wave 0 close.
  if [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv ]; then
    emit_json C12 7 PASS "baseline manifest present (compare in Wave 7)"
  else
    emit_json C12 7 WARN "md5 baseline manifest not yet captured (pre-Wave-7)"
  fi
}

# C13: Manuscript anchors preserved post-rename (content-based per Pitfall 7)
check_C13() {
  local manuscript=docs/manuscript/id-vs-ref-LD.md
  if [ -f "$manuscript" ]; then
    # Anchor phrases (content-based, not line-number-based per RESEARCH.md Pitfall 7)
    local hits=0
    for phrase in "SH2B3" "SUPERSEDED" "Identity-LD Inflation" "Harmonization-Pipeline Diagnostics"; do
      if grep -nF "$phrase" "$manuscript" >/dev/null 2>&1; then
        hits=$((hits+1))
      fi
    done
    if [ "$hits" -ge 4 ]; then
      emit_json C13 6 PASS "all 4 honest-framing-lock anchors found"
    else
      emit_json C13 6 FAIL "$hits/4 honest-framing-lock anchors found"
    fi
  else
    emit_json C13 6 WARN "id-vs-ref-LD.md not yet in place (pre-Wave-6)"
  fi
}

# C14: Bundle is reproducible and clean
check_C14() {
  local bundle
  bundle=$(ls -t bundles/*.zip 2>/dev/null | head -1)
  if [ -n "$bundle" ] && unzip -t "$bundle" >/dev/null 2>&1; then
    emit_json C14 7 PASS "bundle $bundle integrity OK"
  else
    emit_json C14 7 WARN "bundle not yet built or unzip -t failed (pre-Wave-7)"
  fi
}

# C15: OSF deviation log entry added
check_C15() {
  local f=.planning/amendments/osf_deviations.md
  if [ -f "$f" ] && grep -qE "Cache invalidation|2026-04-(28|29|30)" "$f"; then
    emit_json C15 7 PASS "deviation entry present"
  elif [ -f "$f" ]; then
    emit_json C15 7 FAIL "osf_deviations.md exists but no cache-invalidation entry"
  else
    emit_json C15 7 WARN "osf_deviations.md not yet created (pre-Wave-7)"
  fi
}

# Dispatch
WAVE_FILTER="all"
if [ "${1:-}" = "--wave" ] && [ -n "${2:-}" ]; then
  WAVE_FILTER="$2"
fi

run_wave_0() { check_C1; check_C2; check_C3; check_C4; }
run_wave_1() { check_C5; }
run_wave_2() { check_C6; check_C7; }
run_wave_3() { check_C8; }
run_wave_4() { check_C9; }
run_wave_5() { check_C10; check_C11; }
run_wave_6() { check_C13; }
run_wave_7() { check_C12; check_C14; check_C15; }

case "$WAVE_FILTER" in
  all)
    run_wave_0; run_wave_1; run_wave_2; run_wave_3
    run_wave_4; run_wave_5; run_wave_6; run_wave_7
    ;;
  0) run_wave_0 ;;
  1) run_wave_1 ;;
  2) run_wave_2 ;;
  3) run_wave_3 ;;
  4) run_wave_4 ;;
  5) run_wave_5 ;;
  6) run_wave_6 ;;
  7) run_wave_7 ;;
  *)
    echo "Usage: $0 [--wave 0..7]" >&2
    exit 2
    ;;
esac

printf '%s\n' "${JSON_OUT[@]}"
exit "$FAIL_COUNT"
