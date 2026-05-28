#!/usr/bin/env bash
#
# run_forensic_mirror.sh — Extract m3-W1 empty-MT catastrophe forensic
# evidence from the AoU workspace bucket and stage it for mirror to NCSU GPFS.
#
# Context: 2026-05-21 m3-W1 catastrophe ($2,100 lost; 3 cohort MTs empty
# with _SUCCESS markers; full root cause at
# .planning/debug/m3-W1-empty-mt-catastrophe.md). This script preserves
# the bucket-side evidence as an immutable record BEFORE Carter migrates
# his workspace to Researcher Workbench 2.0 (deadline 2026-06-30).
#
# Why: workspace buckets are stable GCS infrastructure (very likely
# survive migration), but Track 1 credit recovery from AoU engineering
# is still pending and the audit trail benefits from a NCSU-side
# immutable copy that's independent of any AoU platform decision.
#
# Also produces the hypothesis-distinguisher mtime data per
# [[feedback_w1_catastrophe_hypothesis_distinguisher]]: if MT #1 and
# MT #2 _SUCCESS mtimes are BEFORE 2026-05-20 22:30:00 UTC (kill time),
# debug-doc Hail-finalize hypothesis holds; if AT or AFTER, Carter's
# kill-as-culprit hypothesis holds.
#
# Usage (run inside AoU env, paused-cluster OK; gsutil-only; <2 min;
# ~$0.05 in egress on the hail.log copy):
#
#   # 0. Open a terminal in the AoU env
#   cd /home/jupyter/coloc_analysis
#   git pull origin m3-W2-aou-deltas   # confirm Track 4 patches present
#   chmod +x .planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/run_forensic_mirror.sh
#
#   # 1. Fire the script (writes outputs to /tmp/forensic_mirror/)
#   .planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/run_forensic_mirror.sh
#
#   # 2. Copy the bundle to a personal bucket OR use Workbench Files UI
#   #    to download to your laptop; then mirror to NCSU GPFS.
#   #
#   #    OPTION A (if AoU allows it, and you have gcloud auth from NCSU):
#   #      gsutil cp /tmp/forensic_mirror/forensic_mirror_$(date -u +%Y%m%dT%H%M%S).tar.gz \
#   #               gs://${WORKSPACE_BUCKET}/forensics/
#   #      # Then from NCSU side:
#   #      gsutil cp gs://${WORKSPACE_BUCKET}/forensics/forensic_mirror_*.tar.gz \
#   #               .planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/
#   #
#   #    OPTION B (download via Workbench Files UI):
#   #      Workbench env → Files → /tmp/forensic_mirror/forensic_mirror_*.tar.gz
#   #      Download to laptop, scp to NCSU into
#   #      .planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/
#
#   # 3. From NCSU side, unpack + commit:
#   cd .planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/
#   tar xzf forensic_mirror_*.tar.gz
#   cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
#   git add .planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/
#   git commit -m "docs(m3-W1): mirror catastrophe forensic evidence to NCSU (pre-RW2.0-migration insurance)"
#   git push origin m3-W2-aou-deltas
#
# After step 3 lands, you have an immutable NCSU-side record of the
# bucket state on 2026-05-2X (whenever you fire this) regardless of
# any future AoU platform change.

set -euo pipefail

# --- env sanity ---
: "${WORKSPACE_BUCKET:?must set WORKSPACE_BUCKET (AoU sets this in env)}"
: "${GOOGLE_PROJECT:?must set GOOGLE_PROJECT (AoU sets this in env)}"

# Strip gs:// prefix if present (per src/python/aou_ld_panel.py _normalize_bucket pattern)
BUCKET="${WORKSPACE_BUCKET#gs://}"
BUCKET="${BUCKET%/}"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="/tmp/forensic_mirror"
mkdir -p "$OUT_DIR"

MANIFEST="$OUT_DIR/MANIFEST-$TS.txt"
{
  echo "# m3-W1 catastrophe forensic mirror — generated $TS"
  echo "# Operator: $(whoami)@$(hostname)"
  echo "# Workspace: $BUCKET"
  echo "# GOOGLE_PROJECT: $GOOGLE_PROJECT"
  echo "# Source: .planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/run_forensic_mirror.sh"
  echo "# Catastrophe context: .planning/debug/m3-W1-empty-mt-catastrophe.md"
  echo "# Hypothesis distinguisher: [[feedback_w1_catastrophe_hypothesis_distinguisher]]"
  echo ""
} > "$MANIFEST"

MTS=(mt_afr_qc.mt mt_afr_pca_selfid_qc.mt mt_eur_qc.mt)

# --- Section 1: per-MT existence + du -s + ls -r + _SUCCESS mtime ---
{
  echo ""
  echo "## Section 1: MT inventory + sizes + key file mtimes"
  echo ""
} >> "$MANIFEST"

for mt in "${MTS[@]}"; do
  MT_URI="gs://$BUCKET/ld/$mt"
  {
    echo ""
    echo "### $mt"
    echo "URI: $MT_URI"
    echo ""
    echo "--- gsutil ls (directory present?) ---"
    gsutil ls "$MT_URI" 2>&1 || echo "(directory absent or inaccessible)"
    echo ""
    echo "--- gsutil du -s (total bytes including all subpaths) ---"
    gsutil du -s "$MT_URI" 2>&1 || echo "(du failed; directory likely absent)"
    echo ""
    echo "--- gsutil du -s entries/entries/parts/ (the W1 catastrophe discriminator) ---"
    gsutil du -s "$MT_URI/entries/entries/parts/" 2>&1 || echo "(entries/entries/parts/ ABSENT — catastrophe pattern confirmed)"
    echo ""
    echo "--- gsutil ls -l _SUCCESS (mtime = hypothesis distinguisher) ---"
    echo "Interpretation: mtime BEFORE 2026-05-20 22:30:00 UTC = debug-doc Hail-finalize hypothesis"
    echo "                mtime AT or AFTER 2026-05-20 22:30:00 UTC = Carter's kill-as-culprit hypothesis"
    gsutil ls -l "$MT_URI/_SUCCESS" 2>&1 || echo "(no _SUCCESS marker — MT directory absent or write never finalized)"
    echo ""
    echo "--- metadata.json.gz parse ---"
    gsutil cat "$MT_URI/metadata.json.gz" 2>/dev/null | gunzip 2>/dev/null \
      | python3 -c "import json,sys; m=json.load(sys.stdin); print(f'  n_partitions: {m.get(\"n_partitions\", m.get(\"partitions\", \"<absent>\"))}'); print(f'  keys: {sorted(m.keys())}')" \
      2>&1 || echo "(metadata.json.gz absent or unreadable)"
    echo ""
  } >> "$MANIFEST"
done

# --- Section 2: rows/rows/parts/ inventory for MT #1 + MT #2 (the 35-byte stub pattern) ---
{
  echo ""
  echo "## Section 2: rows/rows/parts/ first 10 files (verifies 35-byte stub pattern)"
  echo ""
} >> "$MANIFEST"

for mt in mt_afr_qc.mt mt_afr_pca_selfid_qc.mt; do
  MT_URI="gs://$BUCKET/ld/$mt"
  {
    echo ""
    echo "### $mt rows/rows/parts/ inventory"
    echo "Expected per debug doc: ~2,045 files, each ~35 bytes (Parquet column-metadata footer stubs)"
    echo ""
    gsutil ls -l "$MT_URI/rows/rows/parts/" 2>&1 | head -15 || echo "(inventory failed)"
    echo "..."
    echo ""
    echo "Total file count: "
    gsutil ls "$MT_URI/rows/rows/parts/" 2>&1 | wc -l || echo "(count failed)"
  } >> "$MANIFEST"
done

# --- Section 3: bucket-wide inventory ---
{
  echo ""
  echo "## Section 3: bucket-wide inventory (sanity check on total size)"
  echo ""
  echo "Expected per debug doc: bucket total ~71 MiB (27 MiB hail.log preserve + ~44 MiB everything else)."
  echo ""
} >> "$MANIFEST"

{
  echo "--- gsutil du -sh gs://$BUCKET ---"
  gsutil du -sh "gs://$BUCKET" 2>&1 || echo "(du failed)"
  echo ""
  echo "--- top-level directories ---"
  gsutil ls "gs://$BUCKET/" 2>&1 || echo "(listing failed)"
} >> "$MANIFEST"

# --- Section 4: copy hail.log preserve ---
HAIL_LOG_URI="gs://$BUCKET/forensics/hail.log.pre_pd_migration.20260521T201919Z.log"
HAIL_LOG_DEST="$OUT_DIR/hail.log.pre_pd_migration.20260521T201919Z.log"
{
  echo ""
  echo "## Section 4: hail.log preserve copy"
  echo ""
  echo "Source: $HAIL_LOG_URI"
  echo "Local: $HAIL_LOG_DEST"
  echo ""
} >> "$MANIFEST"

if gsutil cp "$HAIL_LOG_URI" "$HAIL_LOG_DEST" 2>&1; then
  echo "(hail.log copied to $HAIL_LOG_DEST)" >> "$MANIFEST"
  echo "Local size: $(stat -c %s "$HAIL_LOG_DEST") bytes" >> "$MANIFEST"
else
  echo "(hail.log copy FAILED — bucket source missing? check inventory above)" >> "$MANIFEST"
fi

# --- Section 5: source code state at time of mirror ---
{
  echo ""
  echo "## Section 5: source code state at time of mirror"
  echo ""
} >> "$MANIFEST"

if [ -d /home/jupyter/coloc_analysis/.git ]; then
  {
    cd /home/jupyter/coloc_analysis
    echo "--- git rev-parse HEAD ---"
    git rev-parse HEAD
    echo ""
    echo "--- git log --oneline -10 ---"
    git log --oneline -10
    echo ""
    echo "--- Track 4 verifier-helper presence ---"
    grep -c "_validate_checkpoint_populated" src/python/aou_ld_panel.py || echo "0"
    echo "--- Track 4 assertion-helper presence ---"
    grep -c "_assert_checkpoint_nonempty" src/python/aou_ld_panel.py || echo "0"
  } >> "$MANIFEST" 2>&1
else
  echo "(no /home/jupyter/coloc_analysis git checkout — running outside expected AoU env layout)" >> "$MANIFEST"
fi

# --- Section 6: produce tarball ---
BUNDLE="$OUT_DIR/forensic_mirror_$TS.tar.gz"
tar -czf "$BUNDLE" -C "$OUT_DIR" \
  "MANIFEST-$TS.txt" \
  "$(basename "$HAIL_LOG_DEST")" 2>/dev/null \
  || tar -czf "$BUNDLE" -C "$OUT_DIR" "MANIFEST-$TS.txt"

# Always emit a short summary to stdout for the operator.
echo "==============================================================="
echo " m3-W1 forensic mirror complete"
echo "==============================================================="
echo ""
echo "Bundle: $BUNDLE"
echo "Bundle size: $(stat -c %s "$BUNDLE") bytes"
echo "Manifest: $MANIFEST"
echo ""
echo "Hypothesis distinguisher result (from Section 1 above):"
for mt in mt_afr_qc.mt mt_afr_pca_selfid_qc.mt; do
  echo ""
  echo "  $mt _SUCCESS mtime:"
  gsutil ls -l "gs://$BUCKET/ld/$mt/_SUCCESS" 2>&1 | tail -1 || echo "    (no _SUCCESS)"
done
echo ""
echo "Next steps:"
echo "  1. Copy bundle to NCSU GPFS via one of:"
echo "     - gsutil cp $BUNDLE gs://$BUCKET/forensics/ (then gsutil cp from NCSU)"
echo "     - Workbench Files UI download to laptop → scp to NCSU"
echo "  2. Land at .planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/"
echo "  3. Untar, git add, commit, push to origin/m3-W2-aou-deltas"
echo "  4. Reply to Abby in Zendesk #57144 noting the mirror is preserved"
echo "  5. Migrate to Researcher Workbench 2.0 at Carter's discretion"
echo ""
