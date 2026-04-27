#!/usr/bin/env bash
# bin/track-a-repro-bundle.sh -- Build a deterministic Track A
# author-reproducibility tarball.
#
# Closes Eval 4B (bidirectional provenance at file boundary) of the 27-item
# Track A audit closure tracker
# (.planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md).
#
# DEC-2026-04-25-01 (.planning/DECISIONS.md:663-677) keeps the ~160 MB
# results_identity_ld/ tree out of git. This script packages the
# identity-LD SuSiE-RSS JSON tree, the canonical K2D summary, the real-LD
# comparator slice and the Fig 3 generator into a single tarball that lets
# an external reviewer regenerate Fig 3 (SH2B3_12q24 EUR collapse forest)
# without re-firing the 95-region SuSiE pipeline (~1 h LSF).
#
# Output is written under results/track-a-bundles/ which is gitignored via
# results/* (.gitignore:88). This script DOES NOT call git add / commit /
# push. The bundle is intended for manual OSF deposit at osf.io/az52u.
#
# Usage:
#   bin/track-a-repro-bundle.sh [--out-dir <path>] [--include-rds] [--dry-run]
#   bin/track-a-repro-bundle.sh -h | --help
#
# Conventions follow bin/bootstrap-conda-envs.sh (shebang, set -euo
# pipefail, PROJECT_ROOT resolution, hardcoded /rs1 conda-env paths).

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# --- Defaults ----------------------------------------------------------------

OUT_DIR="results/track-a-bundles"
INCLUDE_RDS=0
DRY_RUN=0

PYTHON_BIN="/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python"
FREEZE_TOOL="src/python/freeze_sha256_manifest.py"

IDENTITY_FM_DIR="results_identity_ld/fine_mapping"
IDENTITY_MANIFEST="${IDENTITY_FM_DIR}/finemap_manifest.tsv"
K2D_SUMMARY=".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv"
REALLD_SUMMARY="results/fine_mapping/finemap_summary.tsv"
FIG3_R="src/R/figures/fig3_sh2b3_eur_collapse_forest.R"

EXPECTED_JSON_COUNT=95
DETERMINISTIC_MTIME='2026-01-01 00:00:00 UTC'

# --- Argparse ----------------------------------------------------------------

usage() {
  sed -n '2,25p' "$0"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --include-rds)
      INCLUDE_RDS=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[bundle] ERROR: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

log() { echo "[bundle] $*"; }
warn() { echo "[bundle] WARN: $*" >&2; }
die() { echo "[bundle] ERROR: $*" >&2; exit 1; }

# --- Pre-flight --------------------------------------------------------------

log "PROJECT_ROOT: $PROJECT_ROOT"
log "out-dir:      $OUT_DIR"
log "include-rds:  $INCLUDE_RDS"
log "dry-run:      $DRY_RUN"

[ -f "$IDENTITY_MANIFEST" ] || die "missing: $IDENTITY_MANIFEST"
[ -d "$IDENTITY_FM_DIR" ]   || die "missing: $IDENTITY_FM_DIR"
[ -f "$K2D_SUMMARY" ]       || die "missing: $K2D_SUMMARY"
[ -f "$REALLD_SUMMARY" ]    || die "missing: $REALLD_SUMMARY"
[ -f "$FIG3_R" ]            || die "missing: $FIG3_R"
[ -f "$FREEZE_TOOL" ]       || die "missing: $FREEZE_TOOL"

JSON_COUNT=$(find "$IDENTITY_FM_DIR" -maxdepth 2 -type f -name '*.json' | wc -l)
log "identity-LD JSON fits found: $JSON_COUNT"
if [ "$JSON_COUNT" -ne "$EXPECTED_JSON_COUNT" ]; then
  warn "expected $EXPECTED_JSON_COUNT JSON fits, found $JSON_COUNT (proceeding anyway)"
fi

if [ "$INCLUDE_RDS" -eq 1 ]; then
  RDS_COUNT=$(find "$IDENTITY_FM_DIR" -maxdepth 2 -type f -name '*.fit.rds' | wc -l)
  log "identity-LD .fit.rds files found: $RDS_COUNT (will include)"
fi

# Git context (warn-only on dirty tree).
if git rev-parse --short HEAD >/dev/null 2>&1; then
  GIT_SHA="$(git rev-parse --short HEAD)"
  GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  if ! git diff --quiet HEAD 2>/dev/null; then
    warn "git working tree is dirty; bundle git-sha will be the committed HEAD"
  fi
else
  GIT_SHA="nogit"
  GIT_BRANCH="nogit"
  warn "not a git repository; using sha=nogit"
fi
log "git sha:      $GIT_SHA"
log "git branch:   $GIT_BRANCH"

# UTC_DATE pins the bundle filename to the build day (UTC).
UTC_DATE="$(date -u +%Y%m%d)"
# UTC_TS pins BUNDLE_PROVENANCE.txt timestamp to the *commit* time of the
# bundled git_sha rather than wall-clock build time. This makes the
# bundle a pure function of (git_sha, content) so two consecutive builds
# at the same git SHA produce byte-identical tarballs.
if [ "$GIT_SHA" != "nogit" ]; then
  UTC_TS="$(git log -1 --format=%cI "$GIT_SHA" 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
else
  UTC_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi
BUNDLE_NAME="track-a-repro-bundle_${GIT_SHA}_${UTC_DATE}"
BUNDLE_TGZ="${OUT_DIR}/${BUNDLE_NAME}.tar.gz"
log "bundle:       $BUNDLE_TGZ"

# --- Plan the file list ------------------------------------------------------

declare -a STAGE_PAIRS=()
add_pair() {
  # $1 source path (relative to PROJECT_ROOT)
  # $2 destination path (relative to staging root)
  STAGE_PAIRS+=("$1::$2")
}

# Identity-LD JSON tree.
while IFS= read -r -d '' f; do
  rel="${f#./}"
  add_pair "$rel" "$rel"
done < <(cd "$PROJECT_ROOT" && find "./$IDENTITY_FM_DIR" -maxdepth 2 -type f -name '*.json' -print0 | sort -z)

# Optional .fit.rds.
if [ "$INCLUDE_RDS" -eq 1 ]; then
  while IFS= read -r -d '' f; do
    rel="${f#./}"
    add_pair "$rel" "$rel"
  done < <(cd "$PROJECT_ROOT" && find "./$IDENTITY_FM_DIR" -maxdepth 2 -type f -name '*.fit.rds' -print0 | sort -z)
fi

# Identity-LD finemap manifest.
add_pair "$IDENTITY_MANIFEST" "$IDENTITY_MANIFEST"

# Real-LD comparator slice (whole TSV; downstream slices by trait).
add_pair "$REALLD_SUMMARY" "$REALLD_SUMMARY"

# Canonical K2D summary -> bundled under planning/.
add_pair "$K2D_SUMMARY" "planning/IDENTITY-LD-K2D-FIT-SUMMARY.tsv"

# Fig 3 generator (verbatim).
add_pair "$FIG3_R" "$FIG3_R"

# Companion bundle README (single-sourced from bin/track-a-repro-bundle.README.md).
BIN_README="bin/track-a-repro-bundle.README.md"
if [ -f "$BIN_README" ]; then
  add_pair "$BIN_README" "BUNDLE_README.md"
else
  warn "missing $BIN_README; bundle will skip BUNDLE_README.md"
fi

# --- Dry run short-circuit ---------------------------------------------------

if [ "$DRY_RUN" -eq 1 ]; then
  log "DRY-RUN file list (source -> destination):"
  for pair in "${STAGE_PAIRS[@]}"; do
    src="${pair%%::*}"
    dst="${pair##*::}"
    printf '  %s -> %s\n' "$src" "$dst"
  done
  log "DRY-RUN: would write $BUNDLE_TGZ (+ .sha256 sidecar)"
  log "DRY-RUN: total entries: ${#STAGE_PAIRS[@]} (excludes BUNDLE_PROVENANCE.txt + SHA256SUMS.txt)"
  exit 0
fi

# --- Stage -------------------------------------------------------------------

mkdir -p "$OUT_DIR"
STAGING_PARENT="${OUT_DIR}/.staging-$$"
STAGING="${STAGING_PARENT}/track-a-repro-bundle"
mkdir -p "$STAGING"

cleanup() {
  rm -rf "$STAGING_PARENT"
}
trap cleanup EXIT

log "staging at: $STAGING"

for pair in "${STAGE_PAIRS[@]}"; do
  src="${pair%%::*}"
  dst="${pair##*::}"
  dst_full="${STAGING}/${dst}"
  mkdir -p "$(dirname "$dst_full")"
  cp --reflink=auto "$src" "$dst_full"
done

# --- Provenance --------------------------------------------------------------

R_BIN="/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/R"
if [ -x "$R_BIN" ]; then
  R_VERSION="$("$R_BIN" --version 2>/dev/null | head -1 || echo 'r_coloc not invokable')"
else
  R_VERSION="r_coloc env not found at $R_BIN"
fi

if [ -x "$PYTHON_BIN" ]; then
  PY_VERSION="$("$PYTHON_BIN" --version 2>&1 | head -1 || echo 'smoke_dev python not invokable')"
else
  PY_VERSION="smoke_dev python not found at $PYTHON_BIN"
fi

PROV="${STAGING}/BUNDLE_PROVENANCE.txt"
# All fields below are deterministic functions of (git_sha, project_root,
# host, user, R/Py env). Wall-clock build time is intentionally NOT
# recorded so the bundle is byte-stable per commit.
{
  echo "# Track A author-reproducibility bundle -- provenance"
  echo "# (no wall-clock build_utc; commit_utc is the time anchor)"
  echo
  echo "commit_utc:       $UTC_TS"
  echo "build_user:       $(id -un)"
  echo "build_host:       $(hostname -f 2>/dev/null || hostname)"
  echo "git_sha:          $GIT_SHA"
  echo "git_branch:       $GIT_BRANCH"
  echo "project_root:     $PROJECT_ROOT"
  echo "include_rds:      $INCLUDE_RDS"
  echo "json_count:       $JSON_COUNT"
  echo "r_version:        $R_VERSION"
  echo "python_version:   $PY_VERSION"
  echo "smoke_dev_env:    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev"
  echo "r_coloc_env:      /rs1/researchers/c/ckclinto/conda_envs/r_coloc"
  echo "decision_ref:     DEC-2026-04-25-01 (.planning/DECISIONS.md:663-677)"
  echo "audit_ref:        TRACK-A-AUDIT-RESPONSE-2026-04-26.md Eval 4B"
  echo "policy:           no-git-commit; bundle output is gitignored via results/* (.gitignore:88)"
  echo "deterministic:    tar mtime pinned to $DETERMINISTIC_MTIME; gzip -n (no embedded mtime)"
} > "$PROV"

# --- Inner SHA-256 manifest --------------------------------------------------
#
# Two formats, both deterministic (lexicographic byte order via LC_ALL=C):
#   - SHA256SUMS.txt: GNU sha256sum format ("<hash>  <path>"); reviewers
#     verify with `sha256sum -c SHA256SUMS.txt`.
#   - manifest.tsv:   3-col TSV (relative_path | sha256 | bytes) via
#     src/python/freeze_sha256_manifest.py, matching the M1 OSF convention.
# SHA256SUMS.txt and manifest.tsv exclude themselves from their own listings.

log "writing SHA256SUMS.txt (GNU format) and manifest.tsv (TSV)"
SHASUMS="${STAGING}/SHA256SUMS.txt"
MANIFEST_TSV="${STAGING}/manifest.tsv"

(
  cd "$STAGING"
  find . -type f \
    ! -name 'SHA256SUMS.txt' \
    ! -name 'manifest.tsv' \
    -print0 \
    | LC_ALL=C sort -z \
    | xargs -0 sha256sum \
    | sed 's| \./| |' \
    > SHA256SUMS.txt
)

"$PYTHON_BIN" "$FREEZE_TOOL" \
  --root "$STAGING" \
  --out  "$MANIFEST_TSV" \
  --no-mtime \
  --skip-glob 'SHA256SUMS.txt,manifest.tsv,*.partial,*.deferred,.download_complete*'

# --- Tarball -----------------------------------------------------------------

log "creating deterministic tarball (tar --mtime pinned + gzip -n)"
# Pipe through `gzip -n` to suppress the gzip-header mtime/name fields,
# making the .tar.gz byte-identical across builds with identical content.
tar --sort=name \
    --owner=0 --group=0 --numeric-owner \
    --mtime="$DETERMINISTIC_MTIME" \
    --format=ustar \
    -C "$STAGING_PARENT" \
    -cf - \
    track-a-repro-bundle \
  | gzip -n -9 > "$BUNDLE_TGZ"

# --- Outer checksum ----------------------------------------------------------

OUTER_SHA="${BUNDLE_TGZ}.sha256"
( cd "$OUT_DIR" && sha256sum "$(basename "$BUNDLE_TGZ")" > "$(basename "$OUTER_SHA")" )

# --- Summary -----------------------------------------------------------------

BUNDLE_BYTES=$(stat -c '%s' "$BUNDLE_TGZ")
ENTRY_COUNT=$(tar -tzf "$BUNDLE_TGZ" | wc -l)

log "DONE"
log "  bundle:       $BUNDLE_TGZ"
log "  bytes:        $BUNDLE_BYTES"
log "  entries:      $ENTRY_COUNT"
log "  outer sha256: $(cut -d' ' -f1 "$OUTER_SHA")"
log "  sidecar:      $OUTER_SHA"
log "  reminder:     no git commit performed (DEC-2026-04-25-01 + task policy)"
