# Track A Decision-Pending Items — Resolution Log

**Locked:** 2026-05-03 (quick task `260503-vcl`)
**Source:** `docs/manuscript/id-vs-ref-LD.md` §"Decision-pending items (MUST resolve before submission)" (L402-L409, removed in this pass)
**Companion provenance:** `.planning/DECISIONS.md` entries `DEC-2026-05-03-vcl-Item1` through `DEC-2026-05-03-vcl-Item6`

---

## Purpose

This log captures the editorial trail for the 6 submission-blocking items that originally lived inline at the foot of `docs/manuscript/id-vs-ref-LD.md`. Each item is now resolved with explicit provenance pointing back to the GSD quick task or amendment that landed the resolution. The inline section was removed from the manuscript at the Pass 2 atomic commit of quick task `260503-vcl` to lock the manuscript body to publication-ready content; the audit trail lives here and in `DECISIONS.md`.

---

## Item 1 — Venue Choice (LOCKED: Genome Medicine)

**Original wording (manuscript L404):**
> Venue choice locked — Genome Medicine recommended; AJHG fallback.

**Resolution:** Locked. Primary venue is *Genome Medicine* (BMC, IF ≈ 13). Fallback ladder: *AJHG* short report → *Bioinformatics* applications note. bioRxiv preprint Day 1 regardless of venue.

**Provenance:**
- Strategy doc: `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`
- STATE.md "Two-track split" Track A line: "Venue ladder: *Genome Medicine* → *AJHG* short report → *Bioinformatics* Applications Note"
- Bundle build target: `bin/build_id_vs_ref_ld_submission_bundle.sh` (Genome Medicine house style)

**DECISIONS.md anchor:** `DEC-2026-05-03-vcl-Item1`

---

## Item 2 — Aggregator Freeze Date (LOCKED: 2026-05-01 Wave 5 freeze)

**Original wording (manuscript L405):**
> Freeze date for `results/qtl_coloc/tier_assignments.tsv` and `results/multitrait/coloc_summary.tsv` — propose 2026-04-26 freeze after one more verification pass on aggregators.

**Resolution:** Aggregator freeze landed via `/gsd-quick 260501-wdn` (Wave 5 aggregator + figure refresh + frozen numbers). The proposed 2026-04-26 freeze date was advanced to capture the Wave 2 R2 SH2B3 EUR canonical-pair `coloc.susie` re-fire merge (3 Tier-A signals at PP.H4 = 1.0 at rs3184504); the Wave 5 freeze is the canonical post-R2-merge state.

**Provenance:**
- Quick task: `260501-wdn-w5-aggregator-figure-refresh-frozen-numb`
- `results/multitrait/coloc_summary.tsv` md5: `558fca45…` (post-R2-merge: 28 R1 + 9 R2 = 37 rows)
- `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` §Pre-bioRxiv placeholder-fill (2026-04-27) — LIVE block
- Stage 2 SH2B3 anchor `.fit.rds` md5 invariants preserved: bmi.EUR=`462ada6a…`, hypertension.EUR=`8255c1ac…`, stroke.EUR=`a041eecc…`

**DECISIONS.md anchor:** `DEC-2026-05-03-vcl-Item2`

---

## Item 3 — GitHub Repository Name (LOCKED: carter-clinton/coloc_analysis)

**Original wording (manuscript L406):**
> GitHub repo name — choose canonical slug; recommend rename to align with current honest-framing convention; redirect the old URL.

**Resolution:** Canonical repository URL is `https://github.com/carter-clinton/coloc_analysis`. The legacy `The-ASHES-Laboratory` organization slug (preserved verbatim in pre-Pass-1 manuscript L128) was aligned to the canonical URL in Pass 1 of this same quick task (`260503-vcl`, T1 commit). The rename pre-dated the manuscript draft; no URL redirect is needed (the legacy slug never went live as the public-facing repo).

**Provenance:**
- Quick task: `260503-vcl` Pass 1 (T1 commit, `a9d72eb` 2026-05-03)
- STATE.md L23 (project-state header): `**GitHub remote:** https://github.com/carter-clinton/coloc_analysis`
- Manuscript L128 (post-Pass-1 alignment): "Analysis code is available at https://github.com/carter-clinton/coloc_analysis."
- Audit trail row in `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv` (post-Pass-6 regeneration captures the canonical URL inside the bundle)

**DECISIONS.md anchor:** `DEC-2026-05-03-vcl-Item3`

---

## Item 4 — Table 1 Row Count (LOCKED: disclosure-honest empty-row + 3 SH2B3 R2 Tier-A rows)

**Original wording (manuscript L407):**
> Final Table 1 row count (10 or 20) — depends on real-LD survival rate. **Resolved 2026-04-27 via quick-260427-e8n:** Table 1 is a disclosure-honest empty-row table (0 surviving rows at PP.H4 ≥ 0.5; cf. L166 + L272 + `results/track_a_aggregations/table1_surviving_rows.tsv`).

**Resolution:** Already resolved on 2026-04-27 via quick task `260427-e8n` for the R1 slice (28 canonical-locus trait-pair rows, all empty PP.H4 columns under disclosure-honest empty-body framing). Subsequently expanded by Wave 2 R2 SH2B3 EUR canonical-pair re-fire (commit `b3395d9`) which contributed **3 Tier-A rows at PP.H4 = 1.0 at rs3184504** (BMI–hypertension, hypertension–stroke, hypertension–T2D) — see manuscript Table 1 rows 1–3 at L276-278. Final Table 1 = 3 substantive Tier-A rows (Wave 2 R2 SH2B3) + R1 slice empty-body footer.

**Provenance:**
- Quick task (R1 slice): `260427-e8n` (Table 1 empty-row disclosure)
- Wave 2 R2 re-fire commit: `b3395d9`
- Wave 3 outcome decision token: `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE` (recorded in `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` `<decisions>` block)
- Manuscript anchors: L168 (Table 1 narrative), L276-279 (rendered table), L262 (Conclusion §1 SURVIVE callout)
- Aggregated source TSV: `results/track_a_aggregations/table1_surviving_rows.tsv`

**DECISIONS.md anchor:** `DEC-2026-05-03-vcl-Item4`

---

## Item 5 — OSF Amendment Posted (LOCKED: osf.io/az52u 2026-04-24)

**Original wording (manuscript L408):**
> OSF amendment text for the pivot — coordinate with Track B amendment posting per PROJECT-AMENDMENT-2026-04-22 (post after M1 harmonization, before M2 discovery).

**Resolution:** OSF amendment posted on 2026-04-24 as PDF at `osf.io/az52u` via `/gsd-quick 260424-mxp`. The amendment captures the 2026-04-22 two-track reframe (Track A real-LD audit + Track B genome-wide MTAG/CPASSOC discovery) and pre-registers the SuSiE-RSS L-sweep + cache-staleness-test deviations that subsequently landed in Wave 1 + Wave 4. The deviation log was further consolidated into a 10-entry log via quick task `260503-kfq` (Wave 7 closeout) at `.planning/amendments/osf_deviations.md` (entries 8–17 covering the Track B m3 + m2-post-m3 + earlier quick-task cascade).

**Provenance:**
- Initial post: quick task `260424-mxp` (2026-04-24)
- Closeout consolidation: quick task `260503-kfq` (Wave 7 closeout, 2026-05-03)
- OSF DOI: `10.17605/OSF.IO/PVB5J`
- OSF project URL: `osf.io/az52u`
- Local consolidated log: `.planning/amendments/osf_deviations.md`
- Manuscript L128 cross-reference: "Pre-registration: OSF project osf.io/az52u (DOI 10.17605/OSF.IO/PVB5J); deviations logged in `.planning/amendments/osf_deviations.md`."

**DECISIONS.md anchor:** `DEC-2026-05-03-vcl-Item5`

---

## Item 6 — Figure Generation (LOCKED: 5-figure main roster + S2 + S7 all landed)

**Original wording (manuscript L409):**
> Figure generation code — Figure 2, Figure 3, Figure S7, and (per audit-v2 §HQ2) Figure S2 are landed; remaining captioned-but-unrendered slots covered by §Supplementary Figures S1, S3–S6.

**Resolution:** All main-roster figures landed via the quick-task cascade documented below. Figure 4 was demoted to Figure S5 (pathway enrichment non-computable at threshold per Pathway Enrichment Analysis section). Figure S2 (paired-fit structural inflation) and Figure S7 (LD-reference-quality dose-response) landed as audit-driven additions. Figure 5 (variant mechanism + scorecard) is partial-descriptive-only by design (Tier A+B = 0; only Tier C descriptors).

**Per-figure provenance:**

| Figure | Status | Quick task | Build script |
|--------|--------|-----------|--------------|
| Figure 1A (PP.H4 scatter) | Landed | `260424-lpy` + `260425-1vy` | `src/R/figures/fig_1a_*.R` |
| Figure 1B (regional CS panels) | Landed | `260424-p1b` | `src/R/figures/fig_1b_*.R` |
| Figure 2 (CS-yield bar) | Landed | `260424-mqo` | `src/R/figures/fig_2_*.R` |
| Figure 3 (SH2B3 forest + per-trait yield) | Landed | `260425-1vy` | `src/R/figures/fig_3_*.R` |
| Figure 4 (pathway enrichment) | Demoted to Figure S5 | `260424-k2f` (demotion) | n/a (non-computable) |
| Figure 5 (variant mechanism + scorecard) | Partial-descriptive (by design) | (caption-only at this freeze) | (caption-only) |
| Figure S2 (paired-fit structural inflation) | Landed | `260427-azv` | `src/R/figures/fig_s2_paired_fit_structural_inflation.R` |
| Figure S7 (LD-reference-quality dose-response) | Landed | `260425-wa2` (commit `1e4b071`) | `src/R/figures/fig_h3_ld_overlap_dose_response.R` |
| Figures S1, S3, S4, S5, S6 | Caption-only (supplementary placeholder) | n/a | n/a |

**Provenance roll-up:**
- Closeout pass: quick task `260501-wdn` (Wave 5 aggregator + figure refresh + frozen numbers)
- Frozen scalars: `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` §Paired-fit structural inflation (Figure S2, 2026-04-27) — LIVE; §H3 LD-reference-quality dose-response — LIVE
- Manuscript L342-L356 (Figure legends section, all 5 main + S2 + S7 captions render-ready)

**DECISIONS.md anchor:** `DEC-2026-05-03-vcl-Item6`

---

## Stop-After Note

This log is the editorial trail for the Track A submission-readiness pass. It is referenced by the 6 atomic `DEC-2026-05-03-vcl-ItemN` entries in `.planning/DECISIONS.md` and by the Pass 2 atomic commit of quick task `260503-vcl`. No further action required on these 6 items pre-submission — they are LOCKED.
