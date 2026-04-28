#!/usr/bin/env bash
# build_aou_portal_bundle.sh
#
# Assembles the AoU Researcher Workbench portal-paste bundle as a single zip
# containing the RPS workspace registration sub-prompts and the P&P
# (Publications & Presentations) registration paste-ready Markdown.
#
# Outputs:
#   .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-rps-and-pp-registration.zip
#   .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-portal-bundle-build-log.txt
#
# Modeled on bin/build_track_a_submission_bundle.sh (quick-260427-vbq):
#  - mktemp staging dir + trap-cleanup
#  - explicit-filename copies (no recursive directory args)
#  - heredoc-generated README
#  - post-zip count verification with hard-fail asserts
#
# Usage: bin/build_aou_portal_bundle.sh
#
# No CLI args. Re-running regenerates the zip deterministically.

set -euo pipefail
set -x

# --- locate repo root ---
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- input file inventory (explicit, never recursive) ---
RPS_SRC=".planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md"
PP_SRC=".planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/AOU-PP-REGISTRATION.md"

# --- output paths ---
OUT_DIR=".planning/quick/260428-ppz-aou-pp-registration-and-rps-zip"
OUT_ZIP="$OUT_DIR/aou-rps-and-pp-registration.zip"
BUILD_LOG="$OUT_DIR/aou-portal-bundle-build-log.txt"

# --- preflight ---
[[ -f "$RPS_SRC" ]] || { echo "[FATAL] RPS source missing: $RPS_SRC"; exit 2; }
[[ -f "$PP_SRC"  ]] || { echo "[FATAL] P&P source missing: $PP_SRC";  exit 2; }
mkdir -p "$OUT_DIR"

# --- staging dir ---
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
BUNDLE="$STAGE/aou_portal_bundle"
mkdir -p "$BUNDLE"

# --- copy authoritative artifacts (explicit filenames) ---
cp "$RPS_SRC" "$BUNDLE/AOU-WORKBENCH-REGISTRATION.md"
cp "$PP_SRC"  "$BUNDLE/AOU-PP-REGISTRATION.md"

# --- bundle README ---
SOURCE_COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD)"
BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "$BUNDLE/README.md" <<EOF
# AoU Researcher Workbench Portal Bundle

This zip contains paste-ready Markdown documents for two distinct All of Us
Researcher Workbench portal actions:

1. **\`AOU-WORKBENCH-REGISTRATION.md\`** — workspace registration (Research
   Project Summary / RPS) sub-prompts. 13 portal sections matching the AoU
   RPS form 1:1. Paste section-by-section into the workspace creation flow.

2. **\`AOU-PP-REGISTRATION.md\`** — Publications & Presentations (P&P)
   draft registration paste-ready Markdown. Contains TWO stacked P&P
   registration blocks:
   - Block 1 — Track B → *Nature Genetics*
   - Block 2 — M3 → *Scientific Data* (data descriptor; venue locked
     2026-04-28 per DEC-2026-04-28-01)

## Paste order

1. Register the workspace first using \`AOU-WORKBENCH-REGISTRATION.md\`.
   Workspace setup precedes any P&P registration because the P&P record
   references the workspace.

2. After the workspace is approved, file BOTH P&P blocks in
   \`AOU-PP-REGISTRATION.md\` at draft stage. AoU policy
   (\`.planning/amendments/AOU-LD-PIPELINE.md\` §2 P6 + §12 R6) requires
   draft-stage P&P registration before any external submission.

3. Update each P&P record at every major scope change and again at submission
   with the final author list, journal name, and submission date.

## Lock-time decisions still TODO

- **AoU CDR Release version** — locked at workspace setup; populate
  \`AOU-PP-REGISTRATION.md\` §1.6 / §2.6 once decided.
- **ORCID** — populate Author tables in \`AOU-PP-REGISTRATION.md\` §1.2 / §2.2
  before any external submission. Same TODO carried in the Track A submission
  bundle's \`CITATION.cff\` (separate zip).
- **Final BMI EUR primary source** (Loh 2022 vs Yengo 2022 per
  \`PROJECT.md\` "Open human-action items" (b)) — affects Track B
  Methods text but does not block P&P draft registration.

## Char-limit handling

AoU portal field char limits vary. Trim each pasted section to the live
limit at paste time. The plain-language lay summary, methods summary, and
acknowledgments are the most likely fields to require trimming.

## Source provenance

| Field | Value |
|---|---|
| Source repository commit | \`$SOURCE_COMMIT\` |
| Bundle build date (UTC) | \`$BUILD_DATE\` |
| Builder script | \`bin/build_aou_portal_bundle.sh\` |
| Quick task | quick-260428-ppz-aou-pp-registration-and-rps-zip |

## Re-build

From a clean checkout:

\`\`\`bash
git clone <repo-url> coloc_analysis
cd coloc_analysis
bin/build_aou_portal_bundle.sh
# zip lands at .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/
#   aou-rps-and-pp-registration.zip
\`\`\`

The bundle is fully regenerable from the source-of-truth Markdown files
under \`.planning/quick/260426-aow-...\` and \`.planning/quick/260428-ppz-...\`.
EOF

# --- assemble zip (explicit file list; never recursive) ---
ZIP_ABS="$REPO_ROOT/$OUT_ZIP"
rm -f "$ZIP_ABS"
( cd "$STAGE" && zip -r "$ZIP_ABS" "aou_portal_bundle" -X )

# --- post-zip verification ---
ZIP_ENTRIES_FILE_COUNT=$(unzip -l "$ZIP_ABS" | awk '/^[ ]*[0-9]+/ {print $NF}' | grep -E '\.(md)$' | wc -l)
ZIP_TOTAL_LINES=$(unzip -l "$ZIP_ABS" | wc -l)

echo "[VERIFY] zip path: $ZIP_ABS"
echo "[VERIFY] zip .md entries: $ZIP_ENTRIES_FILE_COUNT (expected 3)"
[[ "$ZIP_ENTRIES_FILE_COUNT" -eq 3 ]] || { echo "[FATAL] expected 3 .md files in zip, got $ZIP_ENTRIES_FILE_COUNT"; exit 3; }

unzip -t "$ZIP_ABS" > /dev/null && echo "[VERIFY] unzip -t integrity check: OK"

echo "[VERIFY] zip size:"
ls -lh "$ZIP_ABS"

# --- presence checks for each expected entry ---
for entry in \
  "aou_portal_bundle/AOU-WORKBENCH-REGISTRATION.md" \
  "aou_portal_bundle/AOU-PP-REGISTRATION.md" \
  "aou_portal_bundle/README.md" ; do
  if unzip -l "$ZIP_ABS" | grep -q "$entry"; then
    echo "[VERIFY] present: $entry"
  else
    echo "[FATAL] missing zip entry: $entry"
    exit 4
  fi
done

echo "[INFO] AoU portal bundle assembled successfully."
echo "EXIT_CODE=0"
