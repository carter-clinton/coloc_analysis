#!/usr/bin/env bash
# ==============================================================================
# build_track_a_submission_bundle.sh
#
# Deterministic builder for the Track A *Genome Medicine* submission bundle.
# Produces a single self-contained zip at
#   .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/
#     track_a_genome_medicine_submission.zip
#
# Scope: Track A only. Track B legacy code (src/legacy/, m2_*, m3_*,
# aggregate_genomewide_results.py) is intentionally excluded.
#
# Created by quick-260427-vbq.
# ==============================================================================

set -euo pipefail
set -x

# ---- Locate repo root --------------------------------------------------------
ABS_REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ABS_REPO_ROOT" || ! -d "$ABS_REPO_ROOT/.git" ]]; then
    echo "[FATAL] Not inside a git repo (git rev-parse --show-toplevel failed)." >&2
    exit 1
fi
cd "$ABS_REPO_ROOT"

# Sanity-check we are in coloc_analysis (look for a Track A canary file).
if [[ ! -f "$ABS_REPO_ROOT/docs/manuscript/track_a_pivot.md" ]]; then
    echo "[FATAL] docs/manuscript/track_a_pivot.md not found — wrong repo?" >&2
    exit 1
fi

BUNDLE_NAME="track_a_genome_medicine_submission"
OUT_DIR=".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss"
ABS_OUT_DIR="$ABS_REPO_ROOT/$OUT_DIR"

mkdir -p "$ABS_OUT_DIR"

# ---- Locate pandoc -----------------------------------------------------------
PANDOC_HARDCODED="/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc"
if [[ -x "$PANDOC_HARDCODED" ]]; then
    PANDOC="$PANDOC_HARDCODED"
elif command -v pandoc >/dev/null 2>&1; then
    PANDOC="$(command -v pandoc)"
else
    echo "[FATAL] pandoc not found — bundle build requires pandoc." >&2
    exit 1
fi
echo "[INFO] Using pandoc: $PANDOC"
"$PANDOC" --version | head -1

# ---- Stage directory ---------------------------------------------------------
STAGING="$(mktemp -d -t track_a_bundle.XXXXXX)"
cleanup() { rm -rf "$STAGING"; }
trap cleanup EXIT

ROOT="$STAGING/$BUNDLE_NAME"
mkdir -p \
    "$ROOT" \
    "$ROOT/manuscript" \
    "$ROOT/figures" \
    "$ROOT/supplementary" \
    "$ROOT/scripts/R/aggregators" \
    "$ROOT/scripts/R/figures" \
    "$ROOT/scripts/python"

# ---- Step 2: Render manuscript -----------------------------------------------
# Always copy the .md source.
cp "docs/manuscript/track_a_pivot.md" "$ROOT/manuscript/track_a_pivot.md"

RENDER_PATH=""
PDF_ENGINE_TRIED=()

try_pdf_engine() {
    local engine="$1"
    if command -v "$engine" >/dev/null 2>&1; then
        echo "[INFO] Trying pandoc PDF engine: $engine"
        if "$PANDOC" "docs/manuscript/track_a_pivot.md" \
            -o "$ROOT/manuscript/track_a_pivot.pdf" \
            --standalone --toc \
            --pdf-engine="$engine"; then
            RENDER_PATH="pdf:$engine"
            return 0
        else
            PDF_ENGINE_TRIED+=("$engine:render-failed")
            return 1
        fi
    else
        PDF_ENGINE_TRIED+=("$engine:not-installed")
        return 1
    fi
}

if try_pdf_engine xelatex; then :
elif try_pdf_engine lualatex; then :
elif try_pdf_engine pdflatex; then :
elif try_pdf_engine tectonic; then :
elif try_pdf_engine weasyprint; then :
else
    echo "[INFO] No PDF engine available; rendering HTML fallback."
    echo "[INFO] PDF engines tried: ${PDF_ENGINE_TRIED[*]:-none}"

    # Write minimal CSS for HTML rendering.
    cat > "$ROOT/manuscript/minimal.css" <<'CSS_EOF'
/* minimal.css — readable defaults for the HTML manuscript fallback */
body {
    font-family: "Source Serif Pro", Georgia, "Times New Roman", serif;
    line-height: 1.55;
    max-width: 760px;
    margin: 2.5em auto;
    padding: 0 1.25em;
    color: #1c1c1c;
    background: #fdfdfd;
}
h1, h2, h3, h4 {
    font-family: "Source Sans Pro", "Helvetica Neue", Arial, sans-serif;
    line-height: 1.25;
    margin-top: 1.6em;
}
h1 { font-size: 1.85em; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; }
h2 { font-size: 1.45em; }
h3 { font-size: 1.20em; }
code, pre {
    font-family: "JetBrains Mono", "Fira Code", Menlo, Consolas, monospace;
    font-size: 0.92em;
}
pre { background: #f4f4f4; padding: 0.8em 1em; border-radius: 4px; overflow-x: auto; }
table { border-collapse: collapse; margin: 1em 0; }
th, td { border: 1px solid #bbb; padding: 0.4em 0.7em; }
th { background: #eee; }
a { color: #1455a6; text-decoration: none; }
a:hover { text-decoration: underline; }
blockquote { color: #555; border-left: 3px solid #ccc; margin: 1em 0; padding: 0.2em 1em; }
nav#TOC { font-size: 0.95em; background: #f7f7f7; padding: 0.5em 1em; border-radius: 4px; }
CSS_EOF

    if "$PANDOC" "docs/manuscript/track_a_pivot.md" \
        -o "$ROOT/manuscript/track_a_pivot.html" \
        --standalone --toc \
        --metadata title="Real-LD Re-Analysis of Curated Cardiometabolic Pleiotropy Loci" \
        --css=minimal.css; then
        RENDER_PATH="html:pandoc-fallback"
    else
        echo "[FATAL] Both PDF engines unavailable AND HTML render failed." >&2
        exit 1
    fi
fi

echo "[INFO] Manuscript render path: $RENDER_PATH"

# ---- Step 3: Copy figures (explicit list) ------------------------------------
FIGURES=(
    fig1a_pipeline_schematic.pdf
    fig1a_pipeline_schematic.png
    fig1b_locus_panels.pdf
    fig1b_locus_panels.png
    fig2_cs_yield.pdf
    fig2_cs_yield.png
    fig3_sh2b3_eur_collapse_forest.pdf
    fig3_sh2b3_eur_collapse_forest.png
    fig5_variant_mech_scorecard.pdf
    fig5_variant_mech_scorecard.png
    fig_h3_ld_overlap_dose_response.pdf
    fig_h3_ld_overlap_dose_response.png
    fig_s2_paired_fit_structural_inflation.pdf
    fig_s2_paired_fit_structural_inflation.png
)
for f in "${FIGURES[@]}"; do
    cp "docs/manuscript/figures/$f" "$ROOT/figures/$f"
done

# ---- Step 4: Copy supplementary (9 TSVs + frozen-numbers) --------------------
SUPP_TSVS=(
    yield_redistribution.tsv
    pair_pp_h4_summary.tsv
    table3_admissible_pairs.tsv
    per_trait_pair_distribution.tsv
    eight_hub_fates.tsv
    table1_surviving_rows.tsv
    afr_distribution_summary.tsv
    table4_coloc_error_breakdown.tsv
    pathway_real_ld_disclosure.tsv
)
for t in "${SUPP_TSVS[@]}"; do
    cp "results/track_a_aggregations/$t" "$ROOT/supplementary/$t"
done
cp ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md" "$ROOT/supplementary/TRACK-A-FROZEN-NUMBERS.md"

# ---- Step 5: Copy scripts (explicit lists; no recursive copies) --------------
R_AGG=(
    aggregate_table3_admissible_pairs.R
    aggregate_per_trait_pair_and_hubs.R
    aggregate_table1_pleiotropic_loci.R
)
for s in "${R_AGG[@]}"; do
    cp "src/R/aggregators/$s" "$ROOT/scripts/R/aggregators/$s"
done

R_FIGS=(
    fig1a_pipeline_schematic.R
    fig1b_locus_panels.R
    fig2_cs_yield.R
    fig3_sh2b3_eur_collapse_forest.R
    fig5_variant_mech_scorecard.R
    fig_h3_ld_overlap_dose_response.R
    fig_s2_paired_fit_structural_inflation.R
)
for s in "${R_FIGS[@]}"; do
    cp "src/R/figures/$s" "$ROOT/scripts/R/figures/$s"
done

PY_SCRIPTS=(
    aggregate_coloc_manifest_errors.py
    aggregate_pathway_results.py
    aggregate_qtl_coloc.py
)
for s in "${PY_SCRIPTS[@]}"; do
    cp "src/python/$s" "$ROOT/scripts/python/$s"
done

# ---- Step 6: Generate README.md ---------------------------------------------
BUILD_SHA="$(git rev-parse HEAD)"
BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
BUILD_HOST="$(hostname)"

# Derive the manuscript filename for the README listing.
if [[ -f "$ROOT/manuscript/track_a_pivot.pdf" ]]; then
    MANUSCRIPT_RENDERED="track_a_pivot.pdf"
else
    MANUSCRIPT_RENDERED="track_a_pivot.html (+ minimal.css)"
fi

cat > "$ROOT/README.md" <<README_EOF
# Track A Genome Medicine Submission Bundle

This bundle accompanies the manuscript *Real-LD Re-Analysis of Curated
Cardiometabolic Pleiotropy Loci: Identity-LD Fine-Mapping Systematically
Inflates Cross-Trait Colocalization Evidence*, submitted to *Genome Medicine*
by Carter K. Clinton (NCSU ASHES Lab).

## Contents

\`\`\`
track_a_genome_medicine_submission/
├── README.md                                   # this file
├── LICENSE-CODE                                # MIT (covers scripts/)
├── LICENSE-MANUSCRIPT-AND-DATA                 # CC-BY-4.0 (manuscript+data)
├── CITATION.cff
├── manuscript/
│   ├── track_a_pivot.md                        # source
│   └── ${MANUSCRIPT_RENDERED}     # rendered
├── figures/                                    # 14 files (7 builders × {pdf,png})
│   ├── fig1a_pipeline_schematic.{pdf,png}
│   ├── fig1b_locus_panels.{pdf,png}
│   ├── fig2_cs_yield.{pdf,png}
│   ├── fig3_sh2b3_eur_collapse_forest.{pdf,png}
│   ├── fig5_variant_mech_scorecard.{pdf,png}
│   ├── fig_h3_ld_overlap_dose_response.{pdf,png}      # = Fig S7
│   └── fig_s2_paired_fit_structural_inflation.{pdf,png}
├── supplementary/                              # 9 TSV + 1 .md
│   ├── yield_redistribution.tsv
│   ├── pair_pp_h4_summary.tsv
│   ├── table3_admissible_pairs.tsv
│   ├── per_trait_pair_distribution.tsv
│   ├── eight_hub_fates.tsv
│   ├── table1_surviving_rows.tsv
│   ├── afr_distribution_summary.tsv
│   ├── table4_coloc_error_breakdown.tsv
│   ├── pathway_real_ld_disclosure.tsv
│   └── TRACK-A-FROZEN-NUMBERS.md
└── scripts/
    ├── R/
    │   ├── aggregators/                        # 3 R aggregators
    │   │   ├── aggregate_table3_admissible_pairs.R
    │   │   ├── aggregate_per_trait_pair_and_hubs.R
    │   │   └── aggregate_table1_pleiotropic_loci.R
    │   └── figures/                            # 7 R figure builders
    │       ├── fig1a_pipeline_schematic.R
    │       ├── fig1b_locus_panels.R
    │       ├── fig2_cs_yield.R
    │       ├── fig3_sh2b3_eur_collapse_forest.R
    │       ├── fig5_variant_mech_scorecard.R
    │       ├── fig_h3_ld_overlap_dose_response.R
    │       └── fig_s2_paired_fit_structural_inflation.R
    └── python/                                 # 3 Track-A Python aggregators
        ├── aggregate_coloc_manifest_errors.py
        ├── aggregate_pathway_results.py
        └── aggregate_qtl_coloc.py
\`\`\`

## Source repository

The full pinned Snakemake pipeline (and the Track B work-in-progress, which is
*not* part of this submission) lives at:

  https://github.com/carter-clinton/coloc_analysis.git

This bundle is a curated, self-contained snapshot of just the Track A artefacts
needed to reproduce the manuscript figures and tables.

## Pre-registration

- Root pre-registration: https://osf.io/pvb5j
- M2 amendment / Phase 1 closeout PDF: https://osf.io/az52u

## Reproducibility

The script \`bin/build_track_a_submission_bundle.sh\` in the source repository
regenerates this exact bundle from a clean checkout. To rebuild:

\`\`\`bash
git clone https://github.com/carter-clinton/coloc_analysis.git
cd coloc_analysis
bin/build_track_a_submission_bundle.sh
\`\`\`

The output zip will appear at
\`.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip\`.

## Author

Carter K. Clinton — NCSU ASHES Lab — ORCID: TODO (placeholder; replace before
journal upload).

## License

- Code (\`scripts/\`): MIT — see \`LICENSE-CODE\`.
- Manuscript and data (\`manuscript/\`, \`figures/\`, \`supplementary/\`):
  Creative Commons Attribution 4.0 International (CC-BY-4.0) — see
  \`LICENSE-MANUSCRIPT-AND-DATA\`.

## Build provenance

- Source commit:  ${BUILD_SHA}
- Build date UTC: ${BUILD_DATE}
- Build host:     ${BUILD_HOST}
- Manuscript render path: ${RENDER_PATH}
README_EOF

# ---- Step 7: Generate LICENSE-CODE (MIT) ------------------------------------
cat > "$ROOT/LICENSE-CODE" <<'MIT_EOF'
MIT License

Copyright (c) 2026 Carter K. Clinton

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
MIT_EOF

# ---- Step 8: Generate LICENSE-MANUSCRIPT-AND-DATA (CC-BY-4.0) ---------------
cat > "$ROOT/LICENSE-MANUSCRIPT-AND-DATA" <<'CCBY_EOF'
Creative Commons Attribution 4.0 International (CC BY 4.0)

Copyright (c) 2026 Carter K. Clinton

The manuscript, figures, and supplementary data files in this bundle are
licensed under the Creative Commons Attribution 4.0 International License
(CC BY 4.0).

You are free to:
  - Share — copy and redistribute the material in any medium or format.
  - Adapt — remix, transform, and build upon the material for any purpose,
    even commercially.

Under the following terms:
  - Attribution — You must give appropriate credit, provide a link to the
    license, and indicate if changes were made. You may do so in any
    reasonable manner, but not in any way that suggests the licensor
    endorses you or your use.
  - No additional restrictions — You may not apply legal terms or
    technological measures that legally restrict others from doing anything
    the license permits.

Notices:
  - You do not have to comply with the license for elements of the material
    in the public domain or where your use is permitted by an applicable
    exception or limitation.
  - No warranties are given. The license may not give you all of the
    permissions necessary for your intended use. For example, other rights
    such as publicity, privacy, or moral rights may limit how you use the
    material.

Full legal code:
  https://creativecommons.org/licenses/by/4.0/legalcode

Human-readable summary:
  https://creativecommons.org/licenses/by/4.0/

Suggested attribution:
  Clinton, C. K. (2026). "Real-LD Re-Analysis of Curated Cardiometabolic
  Pleiotropy Loci: Identity-LD Fine-Mapping Systematically Inflates
  Cross-Trait Colocalization Evidence." Submitted to Genome Medicine.
  Licensed under CC BY 4.0.
CCBY_EOF

# ---- Step 9: Generate CITATION.cff ------------------------------------------
cat > "$ROOT/CITATION.cff" <<'CFF_EOF'
cff-version: 1.2.0
message: "If you use this work, please cite it as below."
type: software
title: "Real-LD Re-Analysis of Curated Cardiometabolic Pleiotropy Loci: Identity-LD Fine-Mapping Systematically Inflates Cross-Trait Colocalization Evidence"
authors:
  - given-names: "Carter K."
    family-names: "Clinton"
    affiliation: "NCSU ASHES Lab, North Carolina State University"
    orcid: "TODO"  # placeholder — replace before submission
repository-code: "https://github.com/carter-clinton/coloc_analysis"
url: "https://osf.io/pvb5j"
date-released: "2026-04-27"
license: "MIT AND CC-BY-4.0"
CFF_EOF

# ---- Step 10: Zip up ---------------------------------------------------------
ZIP_PATH="$ABS_OUT_DIR/$BUNDLE_NAME.zip"
# Remove any stale zip first so unzip -l reflects the fresh build.
rm -f "$ZIP_PATH"

(
    cd "$STAGING"
    zip -r -q "$ZIP_PATH" "$BUNDLE_NAME"
)

# ---- Step 11: Post-zip verification -----------------------------------------
echo "[INFO] Verifying zip contents at $ZIP_PATH"
ZIP_LISTING="$(unzip -l "$ZIP_PATH")"
echo "$ZIP_LISTING"

count_pattern() {
    local pat="$1"
    echo "$ZIP_LISTING" | grep -cE "$pat" || true
}

N_FIGURES="$(count_pattern '/figures/[^/]+\.(pdf|png)$')"
N_SUPP="$(count_pattern '/supplementary/[^/]+$')"
N_SCRIPTS_R_AGG="$(count_pattern '/scripts/R/aggregators/[^/]+$')"
N_SCRIPTS_R_FIG="$(count_pattern '/scripts/R/figures/[^/]+$')"
N_SCRIPTS_PY="$(count_pattern '/scripts/python/[^/]+$')"
N_SCRIPTS_TOTAL=$(( N_SCRIPTS_R_AGG + N_SCRIPTS_R_FIG + N_SCRIPTS_PY ))

echo "[VERIFY] figures=$N_FIGURES (expect 14)"
echo "[VERIFY] supplementary=$N_SUPP (expect 10)"
echo "[VERIFY] scripts total=$N_SCRIPTS_TOTAL (expect 13: 3 R-agg + 7 R-fig + 3 py)"
echo "[VERIFY]   scripts/R/aggregators=$N_SCRIPTS_R_AGG (expect 3)"
echo "[VERIFY]   scripts/R/figures=$N_SCRIPTS_R_FIG (expect 7)"
echo "[VERIFY]   scripts/python=$N_SCRIPTS_PY (expect 3)"

[[ "$N_FIGURES" -eq 14 ]] || { echo "[FAIL] figures count mismatch" >&2; exit 1; }
[[ "$N_SUPP"    -eq 10 ]] || { echo "[FAIL] supplementary count mismatch" >&2; exit 1; }
[[ "$N_SCRIPTS_R_AGG" -eq 3 ]] || { echo "[FAIL] scripts/R/aggregators count mismatch" >&2; exit 1; }
[[ "$N_SCRIPTS_R_FIG" -eq 7 ]] || { echo "[FAIL] scripts/R/figures count mismatch" >&2; exit 1; }
[[ "$N_SCRIPTS_PY"    -eq 3 ]] || { echo "[FAIL] scripts/python count mismatch" >&2; exit 1; }

# Root-level required files.
for f in README.md LICENSE-CODE LICENSE-MANUSCRIPT-AND-DATA CITATION.cff; do
    echo "$ZIP_LISTING" | grep -qE "$BUNDLE_NAME/$f$" \
        || { echo "[FAIL] missing root file: $f" >&2; exit 1; }
done

# Manuscript: .md always; .pdf OR .html.
echo "$ZIP_LISTING" | grep -qE "manuscript/track_a_pivot\.md$" \
    || { echo "[FAIL] missing manuscript/track_a_pivot.md" >&2; exit 1; }
echo "$ZIP_LISTING" | grep -qE "manuscript/track_a_pivot\.(pdf|html)$" \
    || { echo "[FAIL] missing rendered manuscript (pdf or html)" >&2; exit 1; }

ZIP_SIZE_BYTES="$(stat -c%s "$ZIP_PATH")"
ZIP_SIZE_MB=$(awk "BEGIN { printf \"%.2f\", $ZIP_SIZE_BYTES / 1048576 }")
echo "[VERIFY] zip size = ${ZIP_SIZE_BYTES} bytes (~${ZIP_SIZE_MB} MB)"
if [[ "$ZIP_SIZE_BYTES" -gt 52428800 ]]; then
    echo "[WARN] zip exceeds 50 MB cap; surface this in SUMMARY (cap = 52428800 B)"
fi

echo "[DONE] Bundle written to: $ZIP_PATH"
echo "[DONE] Manuscript render path: $RENDER_PATH"
