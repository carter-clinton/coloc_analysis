---
phase: quick-260427-vbq
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - bin/build_track_a_submission_bundle.sh
  - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip
  - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt
autonomous: true
requirements:
  - SUBMIT-BUNDLE-VBQ
must_haves:
  truths:
    - "A single zip file exists at .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip containing the seven required components."
    - "The zip contains a rendered manuscript artifact (PDF if any PDF engine is available, else HTML + .md source) plus the original .md source either way."
    - "The zip contains all 14 figure files (7 builders x {pdf,png}) under a figures/ subtree."
    - "The zip contains all 9 supplementary TSVs from results/track_a_aggregations/ plus TRACK-A-FROZEN-NUMBERS.md under a supplementary/ subtree."
    - "The zip contains all 3 R aggregators, all 7 R figure builders, and the 3 Track-A-relevant Python aggregators (aggregate_coloc_manifest_errors.py, aggregate_pathway_results.py, aggregate_qtl_coloc.py) under a scripts/ subtree."
    - "The zip contains README.md, LICENSE-CODE (MIT), LICENSE-MANUSCRIPT-AND-DATA (CC-BY-4.0), and CITATION.cff at the bundle root."
    - "A reproducible build script bin/build_track_a_submission_bundle.sh exists and can regenerate the zip from a clean checkout."
    - "No staged files touch .claude/settings.json, .planning/config.json, .claude/scheduled_tasks.lock, or anything under .planning/phases/m3-aou-afr-ld-panel-build/."
  artifacts:
    - path: "bin/build_track_a_submission_bundle.sh"
      provides: "Deterministic build script that assembles the submission bundle"
      contains: "track_a_genome_medicine_submission.zip"
    - path: ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip"
      provides: "The submission bundle deliverable"
    - path: ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt"
      provides: "Captured stdout/stderr from the build run, including pandoc PDF/HTML decision"
  key_links:
    - from: "bin/build_track_a_submission_bundle.sh"
      to: "docs/manuscript/track_a_pivot.md"
      via: "pandoc render"
      pattern: "pandoc.*track_a_pivot\\.md"
    - from: "bin/build_track_a_submission_bundle.sh"
      to: "results/track_a_aggregations/*.tsv"
      via: "cp into staging dir"
      pattern: "results/track_a_aggregations"
    - from: "track_a_genome_medicine_submission.zip"
      to: "README.md"
      via: "in-archive bundle root"
      pattern: "README\\.md"
---

<objective>
Assemble the Track A *Genome Medicine* submission bundle as a single zip file at
`.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip`,
with a deterministic build script under `bin/` so Carter can re-run the build
from a clean checkout.

Purpose: Track A was venue-locked to *Genome Medicine* in quick-260427-urj
(commit `b4f216e`). This bundle is the deliverable Carter will upload to the
journal portal alongside the cover letter. It must be self-contained:
manuscript + figures + supplementary data + analysis scripts + README + LICENSE
+ CITATION, all in one archive, no missing references.

Output: One zip (~few MB expected, well under the 50 MB cap), one build script,
one build log capturing the pandoc PDF/HTML decision branch.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@docs/manuscript/track_a_pivot.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md

<!-- Pre-flight findings from orchestrator (do not re-discover): -->
<!-- - pandoc 3.8.3 available at /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc -->
<!-- - NO LaTeX engine, NO weasyprint, NO chromium/chrome/firefox installed -->
<!-- - Fallback: pandoc --to=html5 --standalone --toc + ship .md source -->
<!-- - DO NOT pip-install weasyprint or sudo-install LaTeX -->
<!-- - git remote: https://github.com/carter-clinton/coloc_analysis.git -->
<!-- - OSF refs: osf.io/pvb5j (root prereg) + osf.io/az52u (M2 amendment) -->
<!-- - NO existing LICENSE file at repo root; bundle ships MIT (code) + CC-BY-4.0 (manuscript+data) INSIDE zip only -->
<!-- - bin/ directory already exists; precedent: bin/track-a-repro-bundle.sh -->

<bundle_layout>
The zip extracts to a single top-level directory `track_a_genome_medicine_submission/`
with this layout:

```
track_a_genome_medicine_submission/
├── README.md                                    # bundle index (NEW, generated)
├── LICENSE-CODE                                 # MIT (NEW, generated)
├── LICENSE-MANUSCRIPT-AND-DATA                  # CC-BY-4.0 (NEW, generated)
├── CITATION.cff                                 # (NEW, generated)
├── manuscript/
│   ├── track_a_pivot.md                         # source
│   ├── track_a_pivot.html  OR  track_a_pivot.pdf  # rendered (HTML fallback)
│   └── (minimal.css if HTML path)
├── figures/
│   ├── fig1a_pipeline_schematic.{pdf,png}
│   ├── fig1b_locus_panels.{pdf,png}
│   ├── fig2_cs_yield.{pdf,png}
│   ├── fig3_sh2b3_eur_collapse_forest.{pdf,png}
│   ├── fig5_variant_mech_scorecard.{pdf,png}
│   ├── fig_h3_ld_overlap_dose_response.{pdf,png}      # = Fig S7
│   └── fig_s2_paired_fit_structural_inflation.{pdf,png}
├── supplementary/
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
    │   ├── aggregators/
    │   │   ├── aggregate_table3_admissible_pairs.R
    │   │   ├── aggregate_per_trait_pair_and_hubs.R
    │   │   └── aggregate_table1_pleiotropic_loci.R
    │   └── figures/
    │       ├── fig1a_pipeline_schematic.R
    │       ├── fig1b_locus_panels.R
    │       ├── fig2_cs_yield.R
    │       ├── fig3_sh2b3_eur_collapse_forest.R
    │       ├── fig5_variant_mech_scorecard.R
    │       ├── fig_h3_ld_overlap_dose_response.R
    │       └── fig_s2_paired_fit_structural_inflation.R
    └── python/
        ├── aggregate_coloc_manifest_errors.py
        ├── aggregate_pathway_results.py
        └── aggregate_qtl_coloc.py
```
</bundle_layout>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Author bin/build_track_a_submission_bundle.sh — deterministic bundle builder</name>
  <files>bin/build_track_a_submission_bundle.sh</files>
  <action>
Create a single bash script at `bin/build_track_a_submission_bundle.sh` that, when
run from the repo root, produces the submission zip + build log deterministically.
The script is intentionally self-contained — README/LICENSE/CITATION text is
generated by heredocs inside the script (no separate template files).

**Script contract:**
- `#!/usr/bin/env bash` + `set -euo pipefail` + `set -x` (verbose for the build_log)
- Hard-coded ABS_REPO_ROOT detection via `git rev-parse --show-toplevel`; abort if not in this repo.
- Hard-coded `BUNDLE_NAME="track_a_genome_medicine_submission"` and
  `OUT_DIR=".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss"`.
- Builds in a temp staging dir (`mktemp -d`), assembles the layout under
  `$STAGING/$BUNDLE_NAME/`, then `(cd $STAGING && zip -r -q $ABS_REPO_ROOT/$OUT_DIR/$BUNDLE_NAME.zip $BUNDLE_NAME)`.
- Trap-cleans the staging dir on exit.

**Step-by-step what the script must do:**

1. **Locate pandoc:** Prefer `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc` if it exists; else `command -v pandoc`; else hard-fail with a clear message ("pandoc not found — bundle build requires pandoc").

2. **Render manuscript — try PDF first, fall back to HTML:**
   - Always copy `docs/manuscript/track_a_pivot.md` to `$STAGING/$BUNDLE_NAME/manuscript/track_a_pivot.md`.
   - Try PDF: `$PANDOC docs/manuscript/track_a_pivot.md -o $STAGING/.../manuscript/track_a_pivot.pdf --standalone --toc --pdf-engine=xelatex` — but ONLY if `command -v xelatex` succeeds. Else try `--pdf-engine=lualatex`, `--pdf-engine=pdflatex`, `--pdf-engine=tectonic`, `--pdf-engine=weasyprint` in that order; only attempt each if the binary exists.
   - If NO PDF engine available, emit `echo "[INFO] No PDF engine available; rendering HTML fallback."` and run:
     `$PANDOC docs/manuscript/track_a_pivot.md -o $STAGING/.../manuscript/track_a_pivot.html --standalone --toc --metadata title="Real-LD Re-Analysis of Curated Cardiometabolic Pleiotropy Loci" --css=minimal.css`
   - If HTML path: write a minimal `minimal.css` (basic readable CSS, ~30 lines: serif body, monospace code, max-width 760px, modest margins) to `$STAGING/.../manuscript/minimal.css` via heredoc.
   - If both PDF and HTML render fail, hard-fail.
   - Echo the chosen render path to stdout (captured by build_log) so SUMMARY can quote it.

3. **Copy figures** — `cp` each of the 14 files from `docs/manuscript/figures/` into `$STAGING/.../figures/` (explicit list, no glob — easier to grep, easier to verify):
   `fig1a_pipeline_schematic.{pdf,png}`, `fig1b_locus_panels.{pdf,png}`, `fig2_cs_yield.{pdf,png}`, `fig3_sh2b3_eur_collapse_forest.{pdf,png}`, `fig5_variant_mech_scorecard.{pdf,png}`, `fig_h3_ld_overlap_dose_response.{pdf,png}`, `fig_s2_paired_fit_structural_inflation.{pdf,png}`.

4. **Copy supplementary** — `cp` each of the 9 TSVs from `results/track_a_aggregations/` (explicit list) into `$STAGING/.../supplementary/`, then `cp .planning/amendments/TRACK-A-FROZEN-NUMBERS.md` into the same dir.

5. **Copy scripts** — `cp` each of:
   - 3 R aggregators in `src/R/aggregators/` -> `$STAGING/.../scripts/R/aggregators/`
   - 7 R figure builders in `src/R/figures/` -> `$STAGING/.../scripts/R/figures/`
   - 3 Track-A Python aggregators in `src/python/` (`aggregate_coloc_manifest_errors.py`, `aggregate_pathway_results.py`, `aggregate_qtl_coloc.py`) -> `$STAGING/.../scripts/python/`
   - **Explicit filenames; do NOT recursively copy directories** (avoids accidentally pulling Track B legacy or unrelated files).

6. **Generate README.md** at bundle root via heredoc. Contents (markdown):
   - Title: "Track A Genome Medicine Submission Bundle"
   - One-paragraph description: "This bundle accompanies the manuscript *Real-LD Re-Analysis of Curated Cardiometabolic Pleiotropy Loci: Identity-LD Fine-Mapping Systematically Inflates Cross-Trait Colocalization Evidence*, submitted to *Genome Medicine* by Carter K. Clinton (NCSU ASHES Lab)."
   - "Contents" section with the directory tree from `<bundle_layout>` above.
   - "Source repository" section: `https://github.com/carter-clinton/coloc_analysis.git` with note that the full pinned Snakemake pipeline lives there.
   - "Pre-registration" section: `https://osf.io/pvb5j` (root pre-registration) + `https://osf.io/az52u` (M2 amendment / Phase 1 closeout PDF).
   - "Reproducibility" section: pointer to the GitHub repo + note that `bin/build_track_a_submission_bundle.sh` regenerates this exact bundle from a clean checkout.
   - "Author" section: "Carter K. Clinton — NCSU ASHES Lab — ORCID: TODO (placeholder)".
   - "License" section: code under MIT (LICENSE-CODE), manuscript+data under CC-BY-4.0 (LICENSE-MANUSCRIPT-AND-DATA).
   - "Build provenance" section: includes `git rev-parse HEAD` (the script substitutes the actual SHA at build time via `$(git rev-parse HEAD)`), build date `$(date -u +%Y-%m-%dT%H:%M:%SZ)`, hostname.

7. **Generate LICENSE-CODE** (MIT) via heredoc with copyright line "Copyright (c) 2026 Carter K. Clinton" — use the standard OSI MIT text verbatim.

8. **Generate LICENSE-MANUSCRIPT-AND-DATA** (CC-BY-4.0) via heredoc — use the canonical CC-BY-4.0 short legal-code header pointing to https://creativecommons.org/licenses/by/4.0/legalcode plus the human-readable summary; full deed text not required (link is canonical).

9. **Generate CITATION.cff** via heredoc with:
   ```yaml
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
   ```

10. **Zip up** — `(cd "$STAGING" && zip -r -q "$ABS_REPO_ROOT/$OUT_DIR/$BUNDLE_NAME.zip" "$BUNDLE_NAME")`. Use `-q` to keep build_log readable.

11. **Post-zip verification** — list zip contents (`unzip -l`) and assert expected file counts:
    - exactly 14 `figures/*` entries
    - exactly 10 `supplementary/*` entries (9 TSV + 1 .md)
    - exactly 13 `scripts/**` entries (3 R aggregators + 7 R figs + 3 py)
    - README.md, LICENSE-CODE, LICENSE-MANUSCRIPT-AND-DATA, CITATION.cff at root
    - manuscript/track_a_pivot.md present + (track_a_pivot.pdf OR track_a_pivot.html) present
    - print zip size in bytes; warn (not fail) if > 50 MB
    Implementation: pipe `unzip -l "$OUT_DIR/$BUNDLE_NAME.zip"` through `awk`/`grep -c` checks; hard-fail with exit 1 on any count mismatch.

12. **chmod 755** the script itself at the very end of authorship (i.e., after Write, the executor must `chmod +x bin/build_track_a_submission_bundle.sh`).

**Constraint reminders for the executor:**
- Use only stdlib bash + zip + unzip + cp + mkdir + the located pandoc. No node, no npm, no pip-installs, no sudo.
- Do NOT include any path under `src/legacy/`, `m2_*`, `m3_*`, `src/python/aggregate_genomewide_results.py` — Track B is out of scope.
- Do NOT touch `.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`, or anything under `.planning/phases/m3-aou-afr-ld-panel-build/`.
  </action>
  <verify>
    <automated>bash -n bin/build_track_a_submission_bundle.sh && grep -q 'track_a_genome_medicine_submission' bin/build_track_a_submission_bundle.sh && grep -q 'pandoc' bin/build_track_a_submission_bundle.sh && grep -q 'osf.io/pvb5j' bin/build_track_a_submission_bundle.sh && grep -q 'osf.io/az52u' bin/build_track_a_submission_bundle.sh && grep -q 'carter-clinton/coloc_analysis' bin/build_track_a_submission_bundle.sh && test -x bin/build_track_a_submission_bundle.sh</automated>
  </verify>
  <done>
- `bin/build_track_a_submission_bundle.sh` exists, is executable (`chmod +x`), and passes `bash -n` (syntax check).
- Script contains all required heredocs (README, LICENSE-CODE, LICENSE-MANUSCRIPT-AND-DATA, CITATION.cff) and references the right manuscript title, OSF IDs, and GitHub URL.
- Script enumerates figures/TSVs/scripts as explicit filenames (no recursive directory copies for src/).
- Script tries PDF engines in order, falls back to HTML, and writes minimal.css when on the HTML path.
- Script does NOT touch any forbidden path (`.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`, `.planning/phases/m3-aou-afr-ld-panel-build/**`).
- Atomic commit boundary for this task: just `bin/build_track_a_submission_bundle.sh` (explicit `git add bin/build_track_a_submission_bundle.sh`); commit message: `feat(track-a): add Genome Medicine submission bundle build script (quick-260427-vbq)`.
  </done>
</task>

<task type="auto">
  <name>Task 2: Run the build, commit the zip + build log</name>
  <files>
    .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip,
    .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt
  </files>
  <action>
Execute the build script and commit its outputs as a single atomic commit.

**Step-by-step:**

1. **Run the build, capturing all output:**
   ```bash
   cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
   bin/build_track_a_submission_bundle.sh > .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt 2>&1
   echo "EXIT_CODE=$?" >> .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt
   ```
   - The script's `set -x` makes the log self-documenting (every command echoed).
   - Use `tee` if you want progress visible while also capturing: `2>&1 | tee .../build_log.txt` — but this drops exit codes through pipefail; the redirect+capture form above is safer for atomic verification.

2. **Verify the zip materialized and is sane:**
   ```bash
   ZIP=.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip
   test -f "$ZIP" || { echo "ZIP MISSING"; exit 1; }
   unzip -l "$ZIP" | tail -1   # show total file count + size
   ZSIZE=$(stat -c%s "$ZIP")
   echo "Zip size: $ZSIZE bytes"
   if [ "$ZSIZE" -gt 52428800 ]; then echo "[WARN] zip exceeds 50 MB cap — surface in SUMMARY"; fi
   ```

3. **Spot-check a few key entries are inside the zip:**
   ```bash
   unzip -l "$ZIP" | grep -q 'track_a_genome_medicine_submission/README.md' || exit 1
   unzip -l "$ZIP" | grep -q 'track_a_genome_medicine_submission/LICENSE-CODE' || exit 1
   unzip -l "$ZIP" | grep -q 'track_a_genome_medicine_submission/LICENSE-MANUSCRIPT-AND-DATA' || exit 1
   unzip -l "$ZIP" | grep -q 'track_a_genome_medicine_submission/CITATION.cff' || exit 1
   unzip -l "$ZIP" | grep -q 'manuscript/track_a_pivot.md' || exit 1
   unzip -l "$ZIP" | grep -qE 'manuscript/track_a_pivot\.(pdf|html)' || exit 1
   unzip -l "$ZIP" | grep -q 'figures/fig1a_pipeline_schematic.pdf' || exit 1
   unzip -l "$ZIP" | grep -q 'supplementary/TRACK-A-FROZEN-NUMBERS.md' || exit 1
   unzip -l "$ZIP" | grep -q 'scripts/R/aggregators/aggregate_table3_admissible_pairs.R' || exit 1
   unzip -l "$ZIP" | grep -q 'scripts/python/aggregate_coloc_manifest_errors.py' || exit 1
   ```

4. **Determine which render path was taken** (PDF vs HTML) — grep build_log.txt:
   ```bash
   grep -E '(\.pdf|\.html)' .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt | grep -i 'track_a_pivot' | head -5
   ```
   Capture this for the SUMMARY's "deviations" section.

5. **Commit hygiene check before staging:**
   ```bash
   git status --porcelain | grep -E '^\s*[MARCD]+\s+(\.claude/settings\.json|\.planning/config\.json|\.claude/scheduled_tasks\.lock|\.planning/phases/m3-aou-afr-ld-panel-build/)' && { echo "FORBIDDEN PATH DIRTY/STAGED — abort"; exit 1; } || true
   ```
   This fails ONLY if a forbidden path is staged for commit; untracked dirty state of those files is preserved.

6. **Atomic commit** — explicit `git add` per file (NEVER `-A`, `-u`, `.`, or directory args):
   ```bash
   git add .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip
   git add .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt
   git status   # confirm only these two paths staged
   git commit -m "feat(track-a): assemble Genome Medicine submission bundle zip (quick-260427-vbq)"
   ```

**Decision point — zip > 50 MB:** If the cap is exceeded, do NOT silently swallow it. Instead:
   (a) Add a single line `track_a_genome_medicine_submission.zip` to `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/.gitignore` (creating that file).
   (b) Stage the `.gitignore` + `build_log.txt` only (not the zip).
   (c) Note the size + decision in the SUMMARY clearly so Carter knows the zip is local-only and must be re-run from the build script.

   In the expected case (small bundle, well under 50 MB), commit the zip directly per step 6.

**Constraint reminders:**
- Do NOT use `git add -A`, `git add .`, `git add -u`, or directory args.
- Do NOT stage `.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`, or anything under `.planning/phases/m3-aou-afr-ld-panel-build/`.
- Do NOT modify `bin/build_track_a_submission_bundle.sh` here — that was Task 1's commit.
  </action>
  <verify>
    <automated>test -f .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip && test -f .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt && unzip -l .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip | grep -q 'track_a_genome_medicine_submission/README.md' && unzip -l .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip | grep -q 'track_a_genome_medicine_submission/CITATION.cff' && unzip -l .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip | grep -q 'figures/fig_s2_paired_fit_structural_inflation.png'</automated>
  </verify>
  <done>
- Zip exists at the canonical path with all 7 required components.
- build_log.txt exists and records the pandoc render decision (PDF vs HTML).
- All 10 spot-check `unzip -l | grep` assertions pass (or the .gitignore branch is taken with explicit SUMMARY note for >50 MB case).
- Atomic commit landed with message `feat(track-a): assemble Genome Medicine submission bundle zip (quick-260427-vbq)`.
- `git status` shows the three forbidden paths still dirty/untracked (preserved, not staged): `.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`.
- No path under `.planning/phases/m3-aou-afr-ld-panel-build/` was staged or committed.
  </done>
</task>

</tasks>

<verification>
After both tasks land:

1. **Zip integrity:**
   ```bash
   unzip -t .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip
   ```
   Should report "No errors detected".

2. **File-count audit** (the script does this internally; re-verify externally):
   ```bash
   unzip -l .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip | awk '/figures\// {n++} END {print "figures:", n}'
   # Expected: figures: 14
   unzip -l .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip | awk '/supplementary\// {n++} END {print "supplementary:", n}'
   # Expected: supplementary: 10
   unzip -l .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip | awk '/scripts\// && !/scripts\/$/ && !/scripts\/[A-Za-z]+\/$/ {n++} END {print "scripts:", n}'
   # Expected: scripts: 13
   ```

3. **Forbidden-path guard verification:**
   ```bash
   git log -2 --name-only | grep -E '(\.claude/settings\.json|\.planning/config\.json|\.claude/scheduled_tasks\.lock|\.planning/phases/m3-aou-afr-ld-panel-build/)' && echo "VIOLATION" || echo "OK — no forbidden paths in last 2 commits"
   ```

4. **Reproducibility check:** A second run of `bin/build_track_a_submission_bundle.sh` should produce a zip whose `unzip -l` listing matches the committed zip's listing (sizes may vary slightly if pandoc embeds timestamps, but file count + paths must match).
</verification>

<success_criteria>
- One zip file at `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip` containing all 7 required components.
- One executable build script at `bin/build_track_a_submission_bundle.sh` that regenerates the zip deterministically.
- One build log at `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt` capturing the pandoc PDF/HTML decision.
- Two atomic commits: one for the script, one for the zip+log.
- Forbidden paths preserved as dirty/untracked: `.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`.
- No paths under `.planning/phases/m3-aou-afr-ld-panel-build/` staged or committed.
- Track B legacy code (src/legacy/, aggregate_genomewide_results.py, m2_*, m3_*) NOT included in zip.
</success_criteria>

<output>
After completion, create `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/260427-vbq-SUMMARY.md` documenting:
- Whether PDF or HTML render path was taken (cite build_log.txt evidence)
- Final zip size in bytes / MB
- Commit SHAs for the two atomic commits
- License choice rationale (MIT for code + CC-BY-4.0 for manuscript+data, both inside zip only — repo root unchanged)
- ORCID-as-TODO placeholder location (CITATION.cff + README.md author section) — flagged for Carter to fill before journal upload
- Any deviations encountered (e.g., missing PDF engine confirmed, fallback path taken)
- Pointer to the build script for re-runs from clean checkout
</output>
