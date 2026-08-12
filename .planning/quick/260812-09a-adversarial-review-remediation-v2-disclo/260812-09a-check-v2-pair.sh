#!/usr/bin/env bash
# 260812-09a-check-v2-pair.sh
#
# Acceptance harness for the **v2** E-2 outgoing disclosure pair
# (260812-09a-SELECTED-PAIR-correction-v2.md).
#
#   ./260812-09a-check-v2-pair.sh [--only ms|osf|wrap] [--self-test]
#
# Exit 0 = every clause passed. Non-zero = at least one clause failed, or a
# required deliverable is absent (absence is a LOUD FAILURE, never a skip).
#
# ---------------------------------------------------------------------------
# WHY A v2 HARNESS EXISTS (D4, 2026-08-11/12 five-way review)
#
# The v1 harness (260811-oku-check-drafts.sh) was DEFEATED in four ways. This
# one fixes each, and each fix carries its own control that is OBSERVED RED in
# --self-test before any real green is trusted:
#
#   D4-01  v1 asserted a figure was PRESENT IN THE FILE. An APOL1 <-> CXADR
#          label swap would have passed. Here every figure is asserted ADJACENT
#          to its OWN region label, and the OSF table is asserted row-wise
#          (label -> exact, flipped, share on the SAME line).
#          Control: NC-A (ms prose swap), NC-D (osf table swap).
#   D4-02  v1's pooled-alone guard read the WHOLE FILE, so the word "dragged"
#          anywhere satisfied it. Here it is scoped to the EXTRACTED PASTE
#          BLOCK. Controls: NC-E (dragged removed in block) and NC-E2 (removed
#          in block, re-added in an out-of-block comment -- must STILL be red).
#   D4-03  (UN)DISCHARGED is asserted with word boundaries, and the boundary
#          dialect itself is verified at run time (clause WRV-03).
#          Control: NC-I (UNDISCHARGED -> DISCHARGED flip).
#   D4-06  v1's expect_red harness was hard-wired to the ms group: 25 of 29
#          clauses were never observed red. Here EVERY clause group (ms, osf,
#          wrap) carries expect_red coverage.
#
# ---------------------------------------------------------------------------
# GREP DIALECT -- MEASURED ON THIS NODE UNDER THE REAL SCRIPT INTERPRETER.
#
# This script runs under its own shebang, so `grep` resolves to /usr/bin/grep =
# **GNU grep 3.6** (measured 2026-08-11/12 on the NC State node).
#
# ⚠ PROVENANCE, STATED CORRECTLY. An interactive agent shell on this node shows
# a `ugrep` CLI *wrapper* for `grep`. That is a wrapper artifact of the shell,
# NOT the runtime dialect of a script executed through its shebang. Do not
# propagate the ugrep claim into any harness.
#
# ⚠ D4-07 -- FORBIDDEN CONSTRUCT. Inside a POSIX ERE bracket expression, the
# two-character sequence backslash-n is NOT "newline": GNU grep 3.6 reads it as
# the SET {backslash, n}. Measured both directions on this node:
#     printf 'aXb\n' | grep -cE 'a[<bs>n]b'  -> 1   (X is neither \ nor n)
#     printf 'anb\n' | grep -cE 'a[<bs>n]b'  -> 0   (n IS in the set)
# ...where <bs> is a literal backslash. A "not a newline" bracket expression is
# therefore a clause that silently means something else. This script contains
# none, and clause WRV-03 greps THIS FILE to prove it. The forbidden literal is
# assembled at run time from pieces so that the guard cannot self-match.
#
# ⚠ EVERY CLAUSE IS LINE-SCOPED. grep and the adjacency walker are line
# oriented, so the v2 paste blocks are written ONE SENTENCE PER LINE and are not
# hard-wrapped. A required multi-word phrase split across a newline would go red.
#
# ---------------------------------------------------------------------------
# ADJACENCY WINDOWS (characters, on one line, label <-> figure)
#
#   ms prose, five locus pairs .................. 40   (correct distances 9-10;
#                                                       an APOL1<->CXADR swap
#                                                       measures 55+ -> RED)
#   ms prose, SH2B3 anchor/tile-3 split ......... 95   (correct 56 and 84; these
#                                                       sit on their own line)
#   osf table rows .............................. 70   (a table swap moves the
#                                                       label to a line that
#                                                       lacks its figure at all)
#
# BLOCK-LENGTH BOUNDS, AND WHY THEY CHANGED
#
#   ms-correction-v2 : 420-700 words. The v1 clause capped the ms block at
#   120-200 words. The v2 content mandated by A-BLOCKER-1 (the three-join
#   mechanism), A-BLOCKER-3 (three restored bounding elements), A-HIGH-1 (both
#   labelled units) and A-MEDIUM(a) (measurement basis + provenance pointer)
#   does not fit 200 words. The bound was RAISED DELIBERATELY rather than
#   dropping a required clause to fit an inherited number.
#   osf-correction-v2: >= 900 words (v1 bound was >= 250).
#
# EVERY FIGURE IS RE-DERIVED AT RUN TIME from
#   .planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-real-corpus.tsv
#   .planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-track-a-regions.tsv
# and never copied from v1 prose. If a TSV is missing, that is a LOUD FAILURE.
# ---------------------------------------------------------------------------

set -uo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

V2_FILE_DEFAULT="$SCRIPT_DIR/260812-09a-SELECTED-PAIR-correction-v2.md"
CORPUS_TSV="$REPO_ROOT/.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-real-corpus.tsv"
TRACKA_TSV="$REPO_ROOT/.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-track-a-regions.tsv"

MS_ID="ms-correction-v2"
OSF_ID="osf-correction-v2"

FAILS=0
pass()    { printf 'PASS %-8s %s\n' "$1" "$2"; }
fail()    { printf 'FAIL %-8s %s -- %s\n' "$1" "$2" "$3"; FAILS=$((FAILS + 1)); }
verdict() { if [ -z "$3" ]; then pass "$1" "$2"; else fail "$1" "$2" "$3"; fi; }

require_file() { # clause_id path
  if [ ! -f "$2" ]; then
    fail "$1" "deliverable file present" "file not found: $2"
    return 1
  fi
  return 0
}

extract_block() { # file block_id -> block body on stdout (marker lines removed)
  awk -v id="$2" '
    { line = $0; sub(/^[ \t]+/, "", line); sub(/[ \t]+$/, "", line) }
    line == "<!-- PASTE-BEGIN: " id " -->" { inb = 1; next }
    line == "<!-- PASTE-END: "   id " -->" { inb = 0; next }
    inb { print }
  ' "$1"
}

has()      { printf '%s\n' "$2" | grep -qE  -- "$1"; }  # ERE pattern, text
hasF()     { printf '%s\n' "$2" | grep -qF  -- "$1"; }  # fixed string, text
file_has() { grep -qE -- "$1" "$2"; }
file_hasF(){ grep -qF -- "$1" "$2"; }

# adjacency walker: is `fig` within `win` characters of `lab` on some ONE line?
# Line-oriented on purpose (see D4-07: no bracket-negated-newline anywhere).
adj_text() { # text lab fig win  -> 0 = adjacent somewhere
  printf '%s\n' "$1" | awk -v lab="$2" -v fig="$3" -v win="$4" '
    { s = $0; li = index(s, lab); if (li == 0) next
      off = 0; rest = s
      while ((fi = index(rest, fig)) > 0) {
        abs = off + fi; d = abs - li; if (d < 0) d = -d
        if (d <= win) { found = 1; exit }
        rest = substr(rest, fi + 1); off = abs
      }
    }
    END { exit (found ? 0 : 1) }'
}

# row-wise binding: SOME single line carries lab AND every one of the given cells
row_binds() { # text lab cell1 [cell2 ...]  -> 0 = a line carries all of them
  local text="$1" lab="$2"; shift 2
  printf '%s\n' "$text" | awk -v lab="$lab" -v cells="$*" '
    BEGIN { n = split(cells, c, " ") }
    { if (index($0, lab) == 0) next
      ok = 1
      for (i = 1; i <= n; i++) if (index($0, c[i]) == 0) { ok = 0; break }
      if (ok) { found = 1; exit }
    }
    END { exit (found ? 0 : 1) }'
}

commafy() { printf '%s' "$1" | awk '{ x=$0; n=length(x); s=""
    for (i=n; i>0; i--) { s = substr(x,i,1) s; if (((n-i+1)%3==0) && i>1) s = "," s } print s }'; }

# ---------------------------------------------------------------------------
# re-derive every figure from the TSVs (never from v1 prose)
# ---------------------------------------------------------------------------
declare -A L_EXACT L_FLIP L_PCT
POOL_EXACT=""; POOL_FLIP=""; POOL_PCT=""
ANCHOR_EXACT=""; ANCHOR_FLIP=""; ANCHOR_PCT=""
T3_EXACT=""; T3_FLIP=""; T3_PCT=""
TILE_ROWS=""; TILE_AFF=""; TILE_MED=""; TILE_MAX=""
LOCI_N=""; LOCI_AFF=""; LOCI_MED=""; LOCI_MAX=""
PAL_EXACT=""; PAL_FLIP=""; PAL_DROP=""; PAL_PCT=""

derive_figures() {
  local k e f p line
  if [ ! -f "$TRACKA_TSV" ] || [ ! -f "$CORPUS_TSV" ]; then
    printf 'FATAL: measurement TSV missing (%s / %s)\n' "$TRACKA_TSV" "$CORPUS_TSV" >&2
    exit 3
  fi

  while IFS=$'\t' read -r k e f p; do
    L_EXACT["$k"]="$e"; L_FLIP["$k"]="$f"; L_PCT["$k"]="$p"
  done < <(awk -F'\t' 'NR>1 { e[$1]+=$3; f[$1]+=$4 }
      END { for (k in e) { d = e[k]+f[k]; printf "%s\t%d\t%d\t%.2f\n", k, e[k], f[k], f[k]/d*100 } }' "$TRACKA_TSV")

  IFS=$'\t' read -r POOL_EXACT POOL_FLIP POOL_PCT < <(awk -F'\t' 'NR>1 { e+=$3; f+=$4 }
      END { printf "%d\t%d\t%.2f\n", e, f, f/(e+f)*100 }' "$TRACKA_TSV")

  IFS=$'\t' read -r ANCHOR_EXACT ANCHOR_FLIP ANCHOR_PCT < <(awk -F'\t' '
      NR>1 && $1=="SH2B3_12q24" && $2 ~ /tile[12]$/ { e+=$3; f+=$4 }
      END { printf "%d\t%d\t%.2f\n", e, f, f/(e+f)*100 }' "$TRACKA_TSV")

  IFS=$'\t' read -r T3_EXACT T3_FLIP T3_PCT < <(awk -F'\t' '
      NR>1 && $2=="SH2B3_12q24__tile3" { e+=$3; f+=$4 }
      END { printf "%d\t%d\t%.2f\n", e, f, f/(e+f)*100 }' "$TRACKA_TSV")

  IFS=$'\t' read -r TILE_ROWS TILE_AFF TILE_MED TILE_MAX < <(
      awk -F'\t' 'NR>1 && $1=="EUR" { d=$3+$4; if (d>0) print $4/d*100 }' "$CORPUS_TSV" \
      | sort -g \
      | awk -v aff="$(awk -F'\t' 'NR>1 && $1=="EUR" && $4>0' "$CORPUS_TSV" | wc -l)" '
          { a[NR]=$1 }
          END { m = (NR%2) ? a[(NR+1)/2] : (a[NR/2]+a[NR/2+1])/2
                printf "%d\t%d\t%.2f\t%.2f\n", NR, aff, m, a[NR] }')

  IFS=$'\t' read -r LOCI_N LOCI_AFF LOCI_MED LOCI_MAX < <(
      awk -F'\t' 'NR>1 && $1=="EUR" { r=$2; sub(/__tile[0-9]+$/,"",r); sub(/__sub[0-9]+$/,"",r)
            e[r]+=$3; f[r]+=$4 }
          END { for (k in e) printf "%.6f\n", f[k]/(e[k]+f[k])*100 }' "$CORPUS_TSV" \
      | sort -g \
      | awk '{ a[NR]=$1; if ($1>0) aff++ }
             END { m = (NR%2) ? a[(NR+1)/2] : (a[NR/2]+a[NR/2+1])/2
                   printf "%d\t%d\t%.4f\t%.4f\n", NR, aff, m, a[NR] }')

  IFS=$'\t' read -r PAL_EXACT PAL_FLIP PAL_DROP PAL_PCT < <(awk -F'\t' '
      NR>1 && $1=="EUR" { e+=$3; f+=$4; p+=$6 }
      END { printf "%d\t%d\t%d\t%.2f\n", e, f, p, p/(e+f)*100 }' "$CORPUS_TSV")
}

# ---------------------------------------------------------------------------
# clause group: ms
# ---------------------------------------------------------------------------
group_ms() {
  local f="$1"
  require_file "MSV-00" "$f" || return
  local prob b w nb ne r p

  prob=""
  nb=$(grep -cF -- "<!-- PASTE-BEGIN: $MS_ID -->" "$f")
  ne=$(grep -cF -- "<!-- PASTE-END: $MS_ID -->" "$f")
  [ "$nb" = "1" ] || prob="$prob begin=$nb"
  [ "$ne" = "1" ] || prob="$prob end=$ne"
  verdict "MSV-01" "the ms-correction-v2 paste block is present exactly once" "$prob"

  b="$(extract_block "$f" "$MS_ID")"

  prob=""
  w=$(printf '%s\n' "$b" | wc -w)
  { [ "$w" -ge 420 ] && [ "$w" -le 700 ]; } || prob="${w}words (bound 420-700, raised deliberately -- see header)"
  verdict "MSV-02" "ms block length is within the RECORDED v2 bound" "$prob"

  prob=""
  has '^[[:space:]]*#' "$b" && prob="$prob markdown-header"
  has '\|'             "$b" && prob="$prob table-pipe"
  verdict "MSV-03" "journal-ready prose: no header, no table inside the ms block" "$prob"

  # D4-01: each locus figure ADJACENT to ITS OWN label (re-derived from the TSV)
  prob=""
  for r in CXADR_F2RL1_6p21 MC4R_18q21 SH2B3_12q24 APOL1_22q12 FTO_16q12; do
    p="${L_PCT[$r]}%"
    adj_text "$b" "$r" "$p" 40 || prob="$prob $r!~$p"
  done
  verdict "MSV-04" "every locus figure sits within 40 chars of ITS OWN label (label swap -> red)" "$prob"

  prob=""
  adj_text "$b" "SH2B3_12q24" "${ANCHOR_PCT}%" 95 || prob="$prob anchor(${ANCHOR_PCT}%)"
  adj_text "$b" "SH2B3_12q24" "${T3_PCT}%"     95 || prob="$prob tile3(${T3_PCT}%)"
  verdict "MSV-05" "the SH2B3 anchor-vs-tile-3 split is stated next to its label" "$prob"

  prob=""
  hasF "TILE-ROW" "$b" || prob="$prob no-TILE-ROW-label"
  hasF "LOCUS"    "$b" || prob="$prob no-LOCUS-label"
  hasF "$TILE_AFF of $TILE_ROWS" "$b" || prob="$prob tile-count($TILE_AFF of $TILE_ROWS)"
  hasF "$TILE_MED" "$b" || prob="$prob tile-median($TILE_MED)"
  hasF "$TILE_MAX" "$b" || prob="$prob tile-max($TILE_MAX)"
  hasF "$LOCI_AFF of $LOCI_N" "$b" || prob="$prob locus-count($LOCI_AFF of $LOCI_N)"
  hasF "$LOCI_MED" "$b" || prob="$prob locus-median($LOCI_MED)"
  hasF "$LOCI_MAX" "$b" || prob="$prob locus-max($LOCI_MAX)"
  file_hasF 'per-region' "$f" && prob="$prob file:unit-equivocation(per-region)"
  verdict "MSV-06" "BOTH units, each explicitly labelled; the tile median is never called per-region" "$prob"

  prob=""
  hasF 'shipped allele-aware join'      "$b" || prob="$prob (i)no-shipped-join"
  hasF 'ld_allele_join_indices'         "$b" || prob="$prob (i)no-routine-name"
  hasF 'produced every percentage quoted here' "$b" || prob="$prob (i)counter-not-named-as-source"
  hasF 'measured and reported but is deliberately not applied' "$b" || prob="$prob (ii)no-not-applied"
  hasF 'recorded internal decision'     "$b" || prob="$prob (ii)no-recorded-decision"
  hasF 'run_qtl_coloc.R'                "$b" || prob="$prob (ii)no-call-site"
  hasF 'without consulting the alleles' "$b" || prob="$prob (iii)no-finemap-blind-join"
  hasF 'African-ancestry arm alone'     "$b" || prob="$prob (iii)fix-not-scoped-to-AFR"
  hasF 'position-only on the European-ancestry arm today' "$b" || prob="$prob (iii)no-EUR-present-tense"
  verdict "MSV-07" "the mechanism triple (i)/(ii)/(iii) is stated so the code agrees exactly" "$prob"

  prob=""
  hasF 'the analysis code is unchanged by this disclosure' "$b" || prob="$prob no-code-unchanged"
  hasF 'forward analysis plan' "$b" || prob="$prob no-forward-plan-scoping"
  verdict "MSV-08" "A-BLOCKER-3: the analysis code is stated UNCHANGED by this disclosure" "$prob"

  prob=""
  hasF 'not a count of realised errors' "$b" || prob="$prob no-population-bounding"
  hasF 'no posterior probability of colocalization is shown' "$b" || prob="$prob no-PP.H4-bounding"
  verdict "MSV-09" "A-BLOCKER-3: population-not-realised-errors + nothing shown wrong" "$prob"

  prob=""
  for p in 'identity-LD stub' 'use_identity' 'byte-identical' 'bookkeeping'; do
    hasF "$p" "$b" || prob="$prob missing($p)"
  done
  verdict "MSV-10" "the identity-LD-stub caveat is inside the ms block" "$prob"

  prob=""
  hasF 'bindable'        "$b" || prob="$prob no-bindable"
  hasF 'exact + flipped' "$b" || prob="$prob no-denominator"
  verdict "MSV-11" "the bindable (exact + flipped) denominator is stated" "$prob"

  prob=""
  hasF '207 real region variant catalogs' "$b" || prob="$prob no-measurement-basis"
  hasF 'az52u' "$b" || prob="$prob no-provenance-pointer-to-the-paired-OSF-entry"
  verdict "MSV-12" "A-MEDIUM(a): measurement basis + provenance pointer" "$prob"

  prob=""
  hasF 'reported direction of effect'  "$b" || prob="$prob no-reported-direction"
  hasF 'published direction of effect' "$b" && prob="$prob block:published-direction-survives"
  verdict "MSV-13" "A-MEDIUM(b): 'reported' not 'published' direction of effect" "$prob"

  prob=""
  hasF 'hypothesis-driven original research' "$b" || prob="$prob no-original-research-framing"
  hasF 'not a salvage of prior work'         "$b" || prob="$prob no-not-a-salvage-clause"
  verdict "MSV-14" "A-MEDIUM(d): the original-research framing sentence is present" "$prob"

  prob=""
  hasF 'matched on coordinates alone' "$b" && prob="$prob block:false-mechanism-phrase-survives"
  hasF 'ignored the alleles'          "$b" && prob="$prob block:allele-blind-claim-survives"
  verdict "MSV-15" "A-BLOCKER-1: the deleted false mechanism phrasing is GONE from the block" "$prob"
}

# ---------------------------------------------------------------------------
# clause group: osf
# ---------------------------------------------------------------------------
group_osf() {
  local f="$1"
  require_file "OSV-00" "$f" || return
  local prob b w nb ne r p e fl

  prob=""
  nb=$(grep -cF -- "<!-- PASTE-BEGIN: $OSF_ID -->" "$f")
  ne=$(grep -cF -- "<!-- PASTE-END: $OSF_ID -->" "$f")
  [ "$nb" = "1" ] || prob="$prob begin=$nb"
  [ "$ne" = "1" ] || prob="$prob end=$ne"
  verdict "OSV-01" "the osf-correction-v2 paste block is present exactly once" "$prob"

  b="$(extract_block "$f" "$OSF_ID")"

  prob=""
  w=$(printf '%s\n' "$b" | wc -w)
  [ "$w" -ge 900 ] || prob="${w}words (bound >=900)"
  verdict "OSV-02" "osf block length is within the RECORDED v2 bound" "$prob"

  prob=""
  has '^[[:space:]]*#' "$b" && prob="$prob markdown-header"
  verdict "OSV-03" "no markdown header inside the osf paste body" "$prob"

  # D4-01 row-wise: the label, its exact, its flipped and its share on ONE line
  prob=""
  for r in CXADR_F2RL1_6p21 MC4R_18q21 SH2B3_12q24 APOL1_22q12 FTO_16q12; do
    e="$(commafy "${L_EXACT[$r]}")"; fl="$(commafy "${L_FLIP[$r]}")"; p="${L_PCT[$r]}%"
    row_binds "$b" "$r" "$e" "$fl" "$p" || prob="$prob row($r)"
    adj_text  "$b" "$r" "$p" 70        || prob="$prob adj($r)"
  done
  verdict "OSV-04" "each table row BINDS its label to its own exact/flipped/share (swap -> red)" "$prob"

  prob=""
  row_binds "$b" "md5-pinned anchor" "$(commafy "$ANCHOR_EXACT")" "${ANCHOR_PCT}%" || prob="$prob anchor-row"
  row_binds "$b" "tile 3" "$(commafy "$T3_EXACT")" "$(commafy "$T3_FLIP")" "${T3_PCT}%" || prob="$prob tile3-row"
  row_binds "$b" "pooled" "$(commafy "$POOL_EXACT")" "$(commafy "$POOL_FLIP")" "${POOL_PCT}%" || prob="$prob pooled-row"
  verdict "OSV-05" "the SH2B3 split rows and the pooled row carry their re-derived values" "$prob"

  # D4-02 BLOCK-SCOPED pooled-alone guard
  prob=""
  if hasF "${POOL_PCT}%" "$b"; then
    hasF 'dragged' "$b"            || prob="$prob block:no-dragged-down-sentence"
    hasF "${L_PCT[APOL1_22q12]}%" "$b" || prob="$prob block:pooled-without-APOL1-figure"
    hasF "${L_PCT[FTO_16q12]}%"   "$b" || prob="$prob block:pooled-without-FTO-figure"
  fi
  verdict "OSV-06" "the pooled ${POOL_PCT}% is never quoted alone -- guard scoped to the PASTE BLOCK" "$prob"

  prob=""
  hasF "TILE-ROW" "$b" || prob="$prob no-TILE-ROW-label"
  hasF "LOCUS"    "$b" || prob="$prob no-LOCUS-label"
  hasF "$TILE_AFF of the $TILE_ROWS" "$b" || prob="$prob tile-count"
  hasF "$TILE_MED" "$b" || prob="$prob tile-median($TILE_MED)"
  hasF "$TILE_MAX" "$b" || prob="$prob tile-max($TILE_MAX)"
  hasF "$LOCI_AFF of $LOCI_N" "$b" || prob="$prob locus-count"
  hasF "$LOCI_MED" "$b" || prob="$prob locus-median($LOCI_MED)"
  hasF "$LOCI_MAX" "$b" || prob="$prob locus-max($LOCI_MAX)"
  verdict "OSV-07" "A-HIGH-1: BOTH units in the osf body, each explicitly labelled" "$prob"

  prob=""
  hasF 'ld_allele_join_indices' "$b" || prob="$prob (i)no-routine-name"
  hasF 'source of every percentage in this entry' "$b" || prob="$prob (i)counter-not-named-as-source"
  hasF 'not by a defective join' "$b" || prob="$prob (i)no-correct-join-statement"
  hasF 'measured and reported but is deliberately not applied' "$b" || prob="$prob (ii)no-not-applied"
  hasF 'recorded internal decision' "$b" || prob="$prob (ii)no-recorded-decision"
  hasF 'it is not an oversight' "$b" || prob="$prob (ii)no-not-an-oversight"
  hasF 'without consulting the alleles' "$b" || prob="$prob (iii)no-finemap-blind-join"
  hasF 'African-ancestry arm alone' "$b" || prob="$prob (iii)fix-not-scoped-to-AFR"
  hasF 'position-only today' "$b" || prob="$prob (iii)no-EUR-present-tense"
  verdict "OSV-08" "A-BLOCKER-1: which join is which, stated in three parts" "$prob"

  prob=""
  hasF 'apply the orientation the join already computes' "$b" || prob="$prob no-real-remedy-part1"
  hasF 'GRCh38' "$b" || prob="$prob no-GRCh38"
  hasF 'GRCh37' "$b" || prob="$prob no-GRCh37"
  hasF 'gate the change by ancestry' "$b" || prob="$prob no-ancestry-gate"
  hasF 'the join is made allele-aware' "$b" && prob="$prob block:already-shipped-commitment-survives"
  verdict "OSV-09" "A-BLOCKER-2: the REAL three-part remedy, and the already-shipped commitment is gone" "$prob"

  prob=""
  hasF "every affected ancestry's colocalization results that exist at the time the remedy is applied" "$b" \
    || prob="$prob no-all-ancestries-scope"
  hasF 'explicitly including the European-ancestry results that exist today' "$b" || prob="$prob no-explicit-EUR"
  hasF 'the affected African-ancestry results are regenerated' "$b" && prob="$prob block:AFR-only-scope-survives"
  hasF 'E-4' "$b" || prob="$prob no-E-4-bundling"
  hasF 'real, non-identity panel' "$b" || prob="$prob no-condition-bound"
  hasF 'we set no schedule' "$b" || prob="$prob no-schedule-disclaimer"
  verdict "OSV-10" "A-BLOCKER-2: re-report scope covers every ancestry that HAS results, incl. EUR" "$prob"

  prob=""
  hasF 'trsx5' "$b" || prob="$prob no-trsx5-named"
  hasF 'position-based' "$b" || prob="$prob no-position-based-premise"
  hasF 'lockstep' "$b" || prob="$prob no-lockstep-premise"
  hasF 'one-sided drop class' "$b" || prob="$prob no-new-drop-class"
  hasF 'premise update' "$b" || prob="$prob not-reasoned-as-premise-update"
  hasF "$(commafy "$PAL_DROP")" "$b" || prob="$prob no-palindrome-magnitude($(commafy "$PAL_DROP"))"
  hasF "${PAL_PCT}%" "$b" || prob="$prob no-palindrome-share(${PAL_PCT}%)"
  hasF 'dropped_palindromic' "$b" || prob="$prob no-counter-named"
  hasF 'occlusion-exclusion and PSD-regularization commitments are unaffected' "$b" \
    && prob="$prob block:unaffected-assertion-survives"
  verdict "OSV-11" "A-MEDIUM(c): the trsx5 interaction is REASONED and bounded, not asserted away" "$prob"

  prob=""
  for p in 'identity-LD stub' 'use_identity' 'byte-identical' 'bookkeeping'; do
    hasF "$p" "$b" || prob="$prob missing($p)"
  done
  verdict "OSV-12" "the identity-LD-stub caveat is inside the osf block" "$prob"

  prob=""
  for p in '46/182' '25.3' '0.20%' '20.33%' 'externally reported' 'synthetic acceptance fixture' '100-fold'; do
    hasF "$p" "$b" || prob="$prob missing($p)"
  done
  verdict "OSV-13" "the internal-record corrections are carried and correctly labelled" "$prob"

  prob=""
  printf '%s\n' "$b" | grep -qi -- 'no pre-registered number' || prob="$prob no-prereg-number-moved"
  hasF 'TRACK-A-FROZEN-NUMBERS' "$b" || prob="$prob no-frozen-numbers-statement"
  verdict "OSV-14" "no pre-registered number moved; Track A frozen numbers untouched" "$prob"

  prob=""
  for p in 'az52u' 'pvb5j'; do hasF "$p" "$b" || prob="$prob block:missing($p)"; done
  grep -qi -- 'append-only' "$f"            || prob="$prob file:missing(append-only)"
  grep -qi -- 'new supplementary file' "$f" || prob="$prob file:missing(new supplementary file)"
  verdict "OSV-15" "append-only NEW-supplementary-file destination on az52u; prereg pvb5j named" "$prob"

  prob=""
  hasF 'reported direction of effect'  "$b" || prob="$prob no-reported-direction"
  hasF 'published direction of effect' "$b" && prob="$prob block:published-direction-survives"
  hasF 'hypothesis-driven original research' "$b" || prob="$prob no-original-research-framing"
  hasF '(3 tiles)' "$b" || prob="$prob no-(3 tiles)"
  hasF '(3 cells)' "$b" && prob="$prob block:(3 cells)-survives"
  verdict "OSV-16" "A-MEDIUM(b)/(d)/(e): reported-not-published, framing sentence, (3 tiles)" "$prob"

  prob=""
  hasF 'matched on coordinates alone' "$b" && prob="$prob block:false-mechanism-phrase-survives"
  hasF 'ignored the alleles'          "$b" && prob="$prob block:allele-blind-claim-survives"
  verdict "OSV-17" "A-BLOCKER-1: the deleted false mechanism phrasing is GONE from the block" "$prob"

  prob=""
  hasF 'we checked and it is immaterial' "$b" || prob="$prob no-immaterial-refusal"
  hasF 'materially exposed' "$b" || prob="$prob no-two-of-five-statement"
  hasF '207 real region variant catalogs' "$b" || prob="$prob no-measurement-basis"
  hasF 'exact + flipped' "$b" || prob="$prob no-denominator"
  verdict "OSV-18" "the cleared-in-v1 elements survive: refusal, two-of-five, basis, denominator" "$prob"
}

# ---------------------------------------------------------------------------
# clause group: wrap  (the file-level wrapper material around the two blocks)
# ---------------------------------------------------------------------------
group_wrap() {
  local f="$1"
  require_file "WRV-00" "$f" || return
  local prob p forbidden l1 l2 l3

  prob=""
  for p in "$MS_ID" "$OSF_ID"; do
    [ "$(grep -cF -- "<!-- PASTE-BEGIN: $p -->" "$f")" = "1" ] || prob="$prob $p:begin"
    [ "$(grep -cF -- "<!-- PASTE-END: $p -->"   "$f")" = "1" ] || prob="$prob $p:end"
  done
  verdict "WRV-01" "both v2 paste blocks are present exactly once" "$prob"

  # D4-03 word-boundary (UN)DISCHARGED, row-scoped
  prob=""
  l1="$(grep -F -- '**(1)** manuscript paragraph' "$f")"
  l2="$(grep -F -- '**(2)** OSF record entry' "$f")"
  l3="$(grep -F -- '**(3)** LIMITATION vs CORRECTION' "$f")"
  [ -n "$l1" ] || prob="$prob no-obligation-1-row"
  [ -n "$l2" ] || prob="$prob no-obligation-2-row"
  [ -n "$l3" ] || prob="$prob no-obligation-3-row"
  has '\bUNDISCHARGED\b' "$l1" || prob="$prob (1)not-UNDISCHARGED"
  has '\bUNDISCHARGED\b' "$l2" || prob="$prob (2)not-UNDISCHARGED"
  has '\bDISCHARGED\b'   "$l1" && prob="$prob (1)standalone-DISCHARGED"
  has '\bDISCHARGED\b'   "$l2" && prob="$prob (2)standalone-DISCHARGED"
  has '\bDISCHARGED\b'   "$l3" || prob="$prob (3)not-DISCHARGED"
  verdict "WRV-02" "obligation status uses word boundaries: (1)/(2) UNDISCHARGED, (3) DISCHARGED" "$prob"

  # runtime dialect self-checks + D4-07 forbidden-construct self-scan
  prob=""
  printf 'UNDISCHARGED\n' | grep -qE '\bDISCHARGED\b' && prob="$prob boundary-self-matches-UN-form"
  printf 'DISCHARGED\n'   | grep -qE '\bDISCHARGED\b' || prob="$prob boundary-fails-on-bare-form"
  printf '195 of 206\n'   | grep -qE '\b195\b'        || prob="$prob digit-boundary-nomatch"
  printf '1955\n'         | grep -qE '\b195\b'        && prob="$prob digit-boundary-overmatch"
  forbidden="$(printf '[^%s]' '\n')"   # assembled at run time so the guard cannot self-match
  grep -qF -- "$forbidden" "$SCRIPT_PATH" && prob="$prob D4-07-forbidden-bracket-construct-in-this-script"
  verdict "WRV-03" "grep dialect verified at run time + no forbidden bracket construct in this script" "$prob"

  prob=""
  for p in 'A-BLOCKER-1' 'A-BLOCKER-2' 'A-BLOCKER-3' 'A-HIGH-1' \
           'A-MEDIUM (a)' 'A-MEDIUM (b)' 'A-MEDIUM (c)' 'A-MEDIUM (d)' 'A-MEDIUM (e)' 'A-HARNESS'; do
    file_hasF "$p" "$f" || prob="$prob delta-missing($p)"
  done
  file_hasF 'v1 → v2 delta' "$f" || prob="$prob no-delta-table"
  verdict "WRV-04" "the v1 -> v2 delta table names EVERY finding ID" "$prob"

  prob=""
  file_hasF 'PRE-PLACEMENT CHECK' "$f" || prob="$prob no-pre-placement-check"
  file_hasF 'Destination.' "$f" || prob="$prob no-destinations"
  file_hasF 'Discharge condition.' "$f" || prob="$prob no-discharge-conditions"
  file_hasF 'osf_deviations.md' "$f" || prob="$prob no-URL-timestamp-record-condition"
  verdict "WRV-05" "destinations, discharge conditions and the pre-placement journal check" "$prob"

  prob=""
  file_hasF 'No agent posts to OSF' "$f" || prob="$prob no-agent-posts-rule"
  file_hasF "Carter's" "$f" || prob="$prob obligations-not-named-as-Carters"
  verdict "WRV-06" "the no-agent-posts-or-places rule is on the face of the file" "$prob"

  prob=""
  file_hasF '260811-tf3' "$f" || prob="$prob v1-not-named"
  file_hasF 'not to be posted or placed' "$f" || prob="$prob v1-not-marked-do-not-post"
  file_hasF 'byte-untouched' "$f" || prob="$prob v1-not-declared-untouched"
  verdict "WRV-07" "v1 is named, marked superseded history, and declared byte-untouched" "$prob"

  prob=""
  file_hasF 'Never quote the pooled' "$f" || prob="$prob no-pooled-rule"
  file_hasF 'Never cite these as the real-LD exposure' "$f" || prob="$prob no-identity-rule"
  file_hasF 'Never quote a corpus figure without its unit' "$f" || prob="$prob no-unit-rule"
  if file_hasF "${POOL_PCT}%" "$f"; then
    file_hasF 'dragged' "$f" || prob="$prob file:no-dragged-statement"
    file_hasF "${L_PCT[APOL1_22q12]}%" "$f" || prob="$prob file:pooled-without-APOL1"
    file_hasF "${L_PCT[FTO_16q12]}%"   "$f" || prob="$prob file:pooled-without-FTO"
  fi
  verdict "WRV-08" "all three standing number rules, including the new unit rule" "$prob"

  prob=""
  file_hasF 'Check-2' "$f" || prob="$prob no-check-2-boundary"
  file_hasF 'do not fold the two into' "$f" || prob="$prob no-separate-posting-instruction"
  verdict "WRV-09" "the separate-from-Check-2 scope boundary is stated" "$prob"

  prob=""
  file_hasF 'e2-exposure-real-corpus.tsv'    "$f" || prob="$prob no-corpus-tsv-named"
  file_hasF 'e2-exposure-track-a-regions.tsv' "$f" || prob="$prob no-tracka-tsv-named"
  file_hasF '__tile[0-9]+$' "$f" || prob="$prob no-locus-collapse-command"
  file_hasF 'dropped_palindromic' "$f" || prob="$prob no-palindrome-derivation"
  verdict "WRV-10" "the derivation commands and both TSV sources are recorded in the file" "$prob"

  prob=""
  grep -qiE -- '\b(revisions?|cleanup)\b' "$f" && prob="$prob non-original-research-framing-word"
  if grep -qi -- 'salvage' "$f"; then
    [ "$(grep -ci -- 'salvage' "$f")" = "$(grep -ci -- 'not a salvage' "$f")" ] \
      || prob="$prob salvage-used-outside-a-negation"
  fi
  verdict "WRV-11" "original-research framing guard: no 'revision', no 'cleanup', salvage only negated" "$prob"

  prob=""
  file_hasF 'DEC-2026-08-11-e2-framing-correction' "$f" || prob="$prob no-framing-decision-cited"
  file_hasF 'DEC-2026-08-07-e2-orientation-disposition' "$f" || prob="$prob no-disposition-decision-cited"
  verdict "WRV-12" "both governing decisions are cited as standing" "$prob"
}

run_group() { # name file  -- run inside a command substitution so FAILS is local
  case "$1" in
    ms)   group_ms   "$2" ;;
    osf)  group_osf  "$2" ;;
    wrap) group_wrap "$2" ;;
    all)  group_ms "$2"; group_osf "$2"; group_wrap "$2" ;;
  esac
  [ "$FAILS" -eq 0 ]
}

# ---------------------------------------------------------------------------
# --self-test : negative controls, on fixture COPIES of the real v2 file.
# The real file is NEVER mutated.
# ---------------------------------------------------------------------------
ST_FAIL=0

block_range() { # file block_id -> "start,end" (body lines only)
  awk -v id="$2" '
    { l=$0; sub(/^[ \t]+/,"",l); sub(/[ \t]+$/,"",l) }
    l == "<!-- PASTE-BEGIN: " id " -->" { b = NR }
    l == "<!-- PASTE-END: "   id " -->" { print b+1 "," NR-1; exit }
  ' "$1"
}

expect_red() { # label group file clause sole(yes|no)
  local label="$1" grp="$2" file="$3" clause="$4" sole="$5" o r nfail
  o="$(run_group "$grp" "$file")"; r=$?
  nfail=$(printf '%s\n' "$o" | grep -c '^FAIL ')
  printf '\n=== %s : expect %s to go RED%s ===\n' "$label" "$clause" \
    "$([ "$sole" = yes ] && printf ' (and ONLY %s)' "$clause")"
  printf '%s\n' "$o" | grep '^FAIL ' || printf '(no FAIL lines -- CONTROL DEFEATED)\n'
  printf 'exit=%d  fail_clauses=%d\n' "$r" "$nfail"
  if [ "$r" -eq 0 ]; then
    printf 'SELF-TEST ERROR: %s PASSED -- CONTROL DEFEATED. The clause is structurally incapable of its job.\n' "$label"
    ST_FAIL=1
    return
  fi
  if ! printf '%s\n' "$o" | grep -q "^FAIL $clause "; then
    printf 'SELF-TEST ERROR: %s failed, but not on %s.\n' "$label" "$clause"
    ST_FAIL=1
  fi
  if [ "$sole" = yes ] && [ "$nfail" -ne 1 ]; then
    printf 'SELF-TEST ERROR: %s was expected to fail ONLY %s, but %d clauses failed.\n' \
      "$label" "$clause" "$nfail"
    ST_FAIL=1
  fi
}

self_test() {
  local d base out rc msr osr
  if [ ! -f "$V2_FILE_DEFAULT" ]; then
    printf 'SELF-TEST FAILED: the v2 deliverable is absent (%s). Controls mutate COPIES of it.\n' \
      "$V2_FILE_DEFAULT"
    return 2
  fi
  d="$(mktemp -d "${TMPDIR:-/tmp}/v2pair-selftest.XXXXXX")" || return 2
  trap 'rm -rf "$d"' RETURN
  base="$d/base.md"
  cp "$V2_FILE_DEFAULT" "$base"
  msr="$(block_range "$base" "$MS_ID")"
  osr="$(block_range "$base" "$OSF_ID")"

  # ---- positive control ----------------------------------------------------
  out="$(run_group all "$base")"; rc=$?
  printf '\n=== NC-0 (positive control): the untouched v2 file must PASS every group ===\n%s\nexit=%d\n' "$out" "$rc"
  if [ "$rc" -ne 0 ]; then
    printf 'SELF-TEST ERROR: the base fixture does not satisfy its own clauses.\n'
    ST_FAIL=1
  fi

  # ---- group ms ------------------------------------------------------------
  # NC-A  D4-01 THE NAMED CONTROL: APOL1 <-> CXADR label swap inside the ms block.
  cp "$base" "$d/ncA.md"
  sed -i "${msr}s|APOL1_22q12|@@SWAP@@|g; ${msr}s|CXADR_F2RL1_6p21|APOL1_22q12|g; ${msr}s|@@SWAP@@|CXADR_F2RL1_6p21|g" "$d/ncA.md"
  expect_red "NC-A (ms: APOL1 <-> CXADR label swap)" ms "$d/ncA.md" "MSV-04" yes

  # NC-B  the unit labels stripped -- the exact A-HIGH-1 equivocation, re-introduced.
  cp "$base" "$d/ncB.md"
  sed -i "${msr}s|per measurement TILE-ROW|per-region|g; ${msr}s|per LOCUS, collapsing|per region, collapsing|g" "$d/ncB.md"
  expect_red "NC-B (ms: unit labels replaced by the v1 per-region equivocation)" ms "$d/ncB.md" "MSV-06" no

  # NC-C  the code-unchanged sentence deleted (A-BLOCKER-3).
  cp "$base" "$d/ncC.md"
  sed -i "${msr}s|the analysis code is unchanged by this disclosure|the pipeline was updated|" "$d/ncC.md"
  expect_red "NC-C (ms: the code-unchanged statement deleted)" ms "$d/ncC.md" "MSV-08" yes

  # NC-L  mechanism (ii) removed -- the disclosed property vanishes.
  cp "$base" "$d/ncL.md"
  sed -i "${msr}s|measured and reported but is deliberately not applied|applied|" "$d/ncL.md"
  expect_red "NC-L (ms: mechanism (ii) 'measured but not applied' removed)" ms "$d/ncL.md" "MSV-07" yes

  # NC-M  the false v1 mechanism phrasing re-introduced into the block.
  cp "$base" "$d/ncM.md"
  sed -i "${msr}s|without consulting the alleles|matched on coordinates alone and ignored the alleles|" "$d/ncM.md"
  expect_red "NC-M (ms: v1's false mechanism phrasing re-introduced)" ms "$d/ncM.md" "MSV-15" no

  # ---- group osf -----------------------------------------------------------
  # NC-D  D4-01: table label swap. The label lands on a row carrying another
  #       locus's numbers, so the row binding breaks even though every figure
  #       is still present in the file.
  cp "$base" "$d/ncD.md"
  sed -i "${osr}s|APOL1_22q12|@@SWAP@@|g; ${osr}s|CXADR_F2RL1_6p21|APOL1_22q12|g; ${osr}s|@@SWAP@@|CXADR_F2RL1_6p21|g" "$d/ncD.md"
  expect_red "NC-D (osf: APOL1 <-> CXADR table label swap)" osf "$d/ncD.md" "OSV-04" no

  # NC-E  D4-02: pooled figure KEPT, the dragged-down sentence removed IN BLOCK.
  cp "$base" "$d/ncE.md"
  sed -i "${osr}s|dragged|pulled|g" "$d/ncE.md"
  expect_red "NC-E (osf: pooled kept, 'dragged down' removed INSIDE the block)" osf "$d/ncE.md" "OSV-06" yes

  # NC-E2 D4-02 companion: same removal, but the word re-added OUT OF BLOCK.
  #       A file-scoped guard would go green here. This one must STAY red.
  cp "$d/ncE.md" "$d/ncE2.md"
  printf '\n<!-- reviewer note: the pooled figure is dragged down by the two clean regions -->\n' >> "$d/ncE2.md"
  expect_red "NC-E2 (osf: 'dragged' present ONLY out of block -- block scoping)" osf "$d/ncE2.md" "OSV-06" yes

  # NC-F  the already-shipped v1 commitment re-introduced (A-BLOCKER-2).
  cp "$base" "$d/ncF.md"
  sed -i "${osr}s|apply the orientation the join already computes|the join is made allele-aware|" "$d/ncF.md"
  expect_red "NC-F (osf: v1's already-shipped 'the join is made allele-aware')" osf "$d/ncF.md" "OSV-09" no

  # NC-G  the re-report scope reverted to the ancestry with no results.
  cp "$base" "$d/ncG.md"
  sed -i "${osr}s|explicitly including the European-ancestry results that exist today|the affected African-ancestry results are regenerated|" "$d/ncG.md"
  expect_red "NC-G (osf: re-report scope reverted to AFR-only)" osf "$d/ncG.md" "OSV-10" yes

  # NC-H  the trsx5 interaction asserted away instead of reasoned.
  cp "$base" "$d/ncH.md"
  sed -i "${osr}s|premise update|no change at all|g" "$d/ncH.md"
  expect_red "NC-H (osf: trsx5 interaction no longer recorded as a premise update)" osf "$d/ncH.md" "OSV-11" yes

  # NC-N  a corrupted re-derived figure: the palindrome magnitude edited.
  cp "$base" "$d/ncN.md"
  sed -i "${osr}s|144,176|14,176|g" "$d/ncN.md"
  expect_red "NC-N (osf: palindrome magnitude corrupted vs the TSV)" osf "$d/ncN.md" "OSV-11" yes

  # ---- group wrap ----------------------------------------------------------
  # NC-I  D4-03 THE NAMED CONTROL: UNDISCHARGED -> DISCHARGED on obligation (1).
  cp "$base" "$d/ncI.md"
  sed -i 's|⛔ \*\*UNDISCHARGED\*\* — discharges at Carter.s placement|⛔ **DISCHARGED** — discharges at Carter’s placement|' "$d/ncI.md"
  expect_red "NC-I (wrap: obligation (1) UNDISCHARGED -> DISCHARGED)" wrap "$d/ncI.md" "WRV-02" yes

  # NC-J  a delta-table row deleted -- the file-by-file miss the review found.
  cp "$base" "$d/ncJ.md"
  sed -i '/^| \*\*A-MEDIUM (c)\*\* |/d' "$d/ncJ.md"
  expect_red "NC-J (wrap: the A-MEDIUM (c) delta row deleted)" wrap "$d/ncJ.md" "WRV-04" yes

  # NC-K  the no-agent-posts rule removed.
  cp "$base" "$d/ncK.md"
  sed -i 's|No agent posts to OSF|An agent may post to OSF|g' "$d/ncK.md"
  expect_red "NC-K (wrap: the no-agent-posts-or-places rule removed)" wrap "$d/ncK.md" "WRV-06" yes

  # NC-P  the forbidden framing word re-introduced.
  cp "$base" "$d/ncP.md"
  sed -i '0,/^## §3 — before pasting$/s||## §3 — before pasting (this is a revision of the record)|' "$d/ncP.md"
  expect_red "NC-P (wrap: the word 'revision' re-introduced)" wrap "$d/ncP.md" "WRV-11" yes

  printf '\n=== SELF-TEST VERDICT ===\n'
  printf 'controls: NC-A NC-B NC-C NC-L NC-M (ms) | NC-D NC-E NC-E2 NC-F NC-G NC-H NC-N (osf) | NC-I NC-J NC-K NC-P (wrap)\n'
  if [ "$ST_FAIL" -eq 0 ]; then
    printf 'SELF-TEST PASSED: every negative control was OBSERVED RED on its named clause, in every clause group.\n'
    return 0
  fi
  printf 'SELF-TEST FAILED: at least one control did not behave as required (see above).\n'
  return 1
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
ONLY=""
DO_SELF_TEST=0
V2_FILE="$V2_FILE_DEFAULT"
while [ $# -gt 0 ]; do
  case "$1" in
    --only)      ONLY="${2:-}"; shift 2 ;;
    --only=*)    ONLY="${1#--only=}"; shift ;;
    --self-test) DO_SELF_TEST=1; shift ;;
    --file)      V2_FILE="${2:-}"; shift 2 ;;
    -h|--help)
      printf 'usage: %s [--only ms|osf|wrap] [--file PATH] [--self-test]\n' "$(basename "$0")"
      exit 0 ;;
    *) printf 'unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

derive_figures

if [ "$DO_SELF_TEST" -eq 1 ]; then
  self_test
  exit $?
fi

case "$ONLY" in
  ""|all) group_ms "$V2_FILE"; group_osf "$V2_FILE"; group_wrap "$V2_FILE" ;;
  ms)     group_ms   "$V2_FILE" ;;
  osf)    group_osf  "$V2_FILE" ;;
  wrap)   group_wrap "$V2_FILE" ;;
  *)      printf 'unknown --only value: %s (expected ms|osf|wrap)\n' "$ONLY" >&2; exit 2 ;;
esac

printf '\n%d clause failure(s).\n' "$FAILS"
[ "$FAILS" -eq 0 ]
