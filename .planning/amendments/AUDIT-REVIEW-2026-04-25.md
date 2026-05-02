# Track A Audit — Independent Scientific Review

**Subject:** `track_a_2026-04-25` snapshot from `coloc_analysis @ ec86832`
**Reviewed:** 2026-04-25
**Scope:** manuscript (`manuscript/id-vs-ref-LD.md`), planning artifacts (`TRACK-A-FROZEN-NUMBERS.md`, `ID-VS-REF-LD-STRATEGY.md`, `DEC-2026-04-25-01`), reproducibility files (`IDENTITY-LD-K2D-FIT-SUMMARY.tsv`, all 5 figure-builder R scripts, `fire_identity_ld_rerun.sh`), and rendered figures (Fig 1A, 1B, 2, 3, 5).

---

## TL;DR

The manuscript claims a **4.25× inflation** of identity-LD over real-LD SuSiE-RSS credible-set yield (12/96 → 51/96) and frames this as the central methodological finding. **The on-disk evidence in this very snapshot contradicts that claim.** The identity-LD K2D re-fire summary (`reproducibility/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`) — the pipeline-matched comparator the manuscript itself commissioned — shows **48 / 95 non-empty credible sets (~50.5 %)**, statistically indistinguishable from the real-LD 51/96 (~53.1 %). The headline "4.25×" derives from a **stale `12` baseline read out of an old session log** (`STATE.md session continuity`), not from a same-pipeline comparison. This single issue invalidates the manuscript's primary claim.

The remaining issues compound this: SuSiE non-convergence at the flagship SH2B3 locus (4 of 5 EUR traits), `ld_overlap_fraction = 0` at the FTO 16q12 fit that produces the only quantitative real-LD PP.H4 number reported, L=10 saturation artifacts, a 78.9 % QTL-coloc failure rate attributed to a *known variant-ID mismatch fix that "may incompletely propagate"*, and 28/28 empty trait-pair `coloc.susie` outputs. The paper's framing as an "audit" is conceptually correct and methodologically valuable; **the audit needs to be applied to itself before submission.**

---

## Evaluation 1 — Methodological soundness (the comparator problem)

The paper's analytical core is a within-locus identity-LD vs. real-LD head-to-head comparison. For that comparison to mean anything, the two arms must come from **the same pipeline, same SuSiE-RSS configuration, same input sumstats, same admissibility filter** — varying *only* the LD reference.

What the artifacts show:

| Source | Identity-LD non-empty CS | Real-LD non-empty CS |
|---|---|---|
| Manuscript headline (`id-vs-ref-LD.md` L28, L82, L138) | **12 / 96** | 51 / 96 |
| `TRACK-A-FROZEN-NUMBERS.md` L21 (provenance) | "12 / 96 … per **prior STATE.md session continuity**" | 51/96 (Stage 2 fire 2026-04-22) |
| **`IDENTITY-LD-K2D-FIT-SUMMARY.tsv`** (the actual pipeline-matched k2d re-fire, 2026-04-24) | **48 / 95 (50.5 %)** | (n/a — different file) |
| `fig2_cs_yield.R` | 12 hard-coded as `N_IDENTITY_LD_NONEMPTY <- 12L` | 51 derived from disk + asserted equal to 51 |

The k2d re-fire **was commissioned to fix exactly this provenance problem** — see `DEC-2026-04-25-01` and `fire_identity_ld_rerun.sh`, which executes the same Snakefile under `pipeline_identity_overlay.yaml`. When that comparator was run, the identity-LD CS yield came back at 48/95, ~4× higher than the headline `12`. The manuscript does not yet reflect this. `fig2_cs_yield.R` line 60 still hard-codes `12L`, and lines 84–94 enforce a hard-fail if disk drifts from the locked scalar — meaning the figure builder is structurally prevented from picking up the corrected number.

**The 4.25× inflation claim, as currently supported, is an artifact of comparing a same-pipeline real-LD run to a different-vintage, different-configuration identity-LD scalar pulled from a session log.** The actual within-pipeline contrast is closer to **1.05×**, which is no inflation at all.

Supporting literature: Kanai et al., *Cell Genomics* 2022 ("Meta-analysis fine-mapping is often miscalibrated at single-variant resolution") shows that LD-reference miscalibration acts on PIP/credible-set composition, not credible-set count per se. Zou et al., *PLoS Genet* 2022 (SuSiE-RSS) explicitly recommends comparing fits with matched configurations.

---

## Evaluation 2 — Statistical rigor (SuSiE convergence, L-saturation, and non-converged fits in headline counts)

Three problems, all visible on the disk evidence:

**(a) Non-convergence treated as data.** Figure 3 shows that under real-LD at SH2B3 EUR, **4 of 5 traits return `status = non_converged`** (BMI, hypertension, stroke; only asthma and T2D = `ok`). SuSiE-RSS's posterior credible sets are only theoretically meaningful at convergence (Wang, Sarkar, Carbonetto & Stephens, *JRSS-B* 2020; Zou et al., *PLoS Genet* 2022). Yet the figure script (`fig3…R` lines 107–113) bakes the non-converged CS counts into the plotted "yield" and the manuscript counts them in the 51/96 headline. The honest read is "SuSiE-RSS failed to converge at most SH2B3 traits under the supplied real-LD reference" — a numerical/algorithmic finding, not biological evidence of "credible-set collapse."

**(b) L = 10 saturation artifacts, undisclosed.** `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` shows ≥11 fits returning `n_CS = 10` with the signature `cs_sizes = "3;3;3;3;3;3;3;3;3;4"` — the absolute floor on credible-set size (3, the SuSiE purity-filter minimum) saturated at the maximum L. This is the canonical fingerprint of L-saturated fits that the SuSiE/SuSiE-RSS authors warn against (Zou et al. 2022 §Discussion: "set L generously and verify n_CS << L"). Such fits should be re-run at L = 20 or 30 and inspected for stability; the manuscript reports the L = 10 numbers as if they were settled posteriors.

**(c) Coloc on uncertain credible sets.** `coloc.susie` (Wallace 2021) is mathematically a credible-set-level integral. When CSes are L-saturated or come from non-converged fits, the resulting PP.H4 inherits that uncertainty without a confidence statement. Figure 3 admits no CIs are plotted because "the production manifest does not store posterior intervals" — the right move, but the absence of intervals also means readers cannot judge whether 0.0517 vs 0.3099 is meaningful or noise.

---

## Evaluation 3 — Data integrity and pipeline correctness (the things that look "off")

A non-exhaustive list of what doesn't add up between the prose and the data:

1. **`ld_overlap_fraction = 0` for the headline real-LD result.** `fig1b_locus_panels.R` lines 33–38 disclose: *"Real-LD overlap at FTO_16q12 EUR Stage 2 fit: ld_overlap_fraction = 0 (ld_status = 'variants_exceed_threshold'). SuSiE effectively fell back toward an identity-like internal structure at this region."* This fit produces the **only quantitative "real-LD" PP.H4 reported in the manuscript** (FTO/IRX3 = 0.3099, abstract L28, headline result). The real-LD branding for that number is materially incorrect.

2. **78.9 % QTL-coloc failure attributed to an unfixed bug.** 1,005 / 1,274 attempts return `too_few_snps`, traced to a "harmonized-TSV vs Phase 1 SuSiE-fit variant-ID format mismatch (chr:pos vs rsid)" with the candid disclosure that "the fix may incompletely propagate to all source × tissue × gene combinations" (`id-vs-ref-LD.md` L60, L180). This is not a Limitations-section caveat — it means **the analysis was published with the knowledge that the data on the y-axis is of unverified quality**.

3. **28/28 empty `coloc.susie` outputs.** All 28 trait-pair attempts returned empty `PP.H3 / PP.H4 / n_snps`. This is interpreted as "consistent with credible-set collapse." But variant-ID format mismatch (item 2) and SuSiE non-convergence (Eval 2) both produce the *same* empty-output signature, so the interpretation is unidentifiable from the data.

4. **The flagship "SH2B3 collapse" is a missing run, not a collapse.** The manuscript states (L146, L278–279) that the canonical BMI–HTN and HTN–stroke trait pairs at SH2B3 EUR are "absent from the Stage 2 `coloc.susie` output manifest." Both `TRACK-A-FROZEN-NUMBERS.md` L51 and the manuscript itself acknowledge this: only `SH2B3_12q24__EUR__asthma_vs_t2d` was actually run. The pre-registered "supplementary re-fire" required to test the actual claim has not happened. Reporting "absent from manifest" as "consistent with credible-set collapse" is overreach — those pairs were simply not executed.

5. **Frozen-numbers TSV row count vs. headline denominator.** The summary TSV has **95 rows**, the manuscript's denominator is **96**. Trivial individually, but symptomatic: figure scripts hard-fail on `nrow(df) == 96` (`fig2…R` L79), so the snapshot's TSV cannot drive the figure. Either the TSV is a 95-row subset or the manuscript denominator drifted by one — the discrepancy is undocumented.

6. **`ld_overlap = 0` on every row of the identity-LD TSV.** Expected for identity-LD (no LD reference is loaded), but the column being present and zero-filled with a `ld_overlap_fraction` column that's also zero means the schema is shared with the real-LD output — verify the schema confusion isn't masking a parse bug.

7. **HLA double-classified.** `id-vs-ref-LD.md` L80 lists HLA_6p21 in the **identity-LD fallback** scope (a region where the paper would still draw conclusions); L102 lists HLA in the **pre-specified negative-control set** ("HLA-immune"). HLA cannot be simultaneously a fallback test region and a definitionally-null control. The "224 negative-control rows resolved to Tier C or empty" claim (L102, L186) becomes near-tautological if a region is classified negative *a priori*.

8. **"Negative-control rows" is region × gene × tissue × trait, not "regions."** 224 rows = 120 cosmetic + 80 blood group + 24 HLA, but the unique locus count is ~5 cosmetic + 4 blood group + 1 HLA = 10 distinct loci. Calling 224 "region-pair evaluations" (TRACK-A-FROZEN, manuscript L102) overstates the breadth of the negative-control panel.

9. **GWAS-vintage / sample-size table inconsistencies.** Manuscript L54: "T2D from DIAMANTE (N ≈ 900,000)." DIAMANTE 2020 (Vujkovic) effective N is ~228k cases / ~1.3M total (mixed-ancestry); the EUR-only subset Mahajan 2018 is N ≈ 898,130. The number is plausible but not unambiguous; verify the citation matches the exact sumstats file used (the harmonized-sumstats path `data/processed/sumstats_harmonized/t2d.EUR.tsv.bgz` doesn't disclose vintage in its filename).

10. **`1,446 attempted tests / 861 failures` ghost numbers.** `TRACK-A-FROZEN-NUMBERS.md` L53 explicitly flags these as not matching disk; `ID-VS-REF-LD-STRATEGY.md` (the abstract draft, L37) still uses them. Confirm they are fully purged before submission — a single relict appearance would be a credibility catastrophe.

---

## Evaluation 4 — Reproducibility & auditability (where the workflow helps and where it hurts)

Strengths: Snakemake-pinned (7.32.4), conda envs frozen (`smoke_dev`, `la_multitrait_r`), R 4.4.2, ggplot2 4.0.1, OSF pre-registration with deviation log, deterministic-sorted summary TSV, and figure scripts that disclose their own data sources. This is rare and good.

Two structural concerns:

**(a) "Locked scalars" prevent self-correction.** `fig2_cs_yield.R` lines 84–94 and `fig3…R` lines 130–140 hard-fail if disk-derived numbers drift from constants set in the script. The intent — preventing silent regression — is admirable, but this discipline pins figures to the *original* numbers even when a re-fire (such as the k2d identity-LD re-fire) yields more accurate ones. The build system enforces a kind of **numeric immutability that becomes adversarial when the original number was wrong**. The manuscript is now in exactly that state for `N_IDENTITY_LD_NONEMPTY`.

**(b) Bidirectional provenance stops at the file boundary.** `fig3…R` reads `results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json` per L48-49, but the snapshot ships only the summary TSV (the binary tree is intentionally regenerable in ~1h, per `DEC-2026-04-25-01`). A reviewer who runs only what is in the snapshot **cannot regenerate Figure 3**. Workable, but raises the cost of independent verification beyond what most reviewers will spend.

References for evaluation context: Pasaniuc & Price, *Nat Rev Genet* 2017, on LD-reference panel size requirements (n = 503 EUR, n = 661 AFR are below the recommended thresholds for stable summary-statistic fine-mapping); Benner et al., *AJHG* 2017, on small-panel LD-mismatch artifacts.

---

## Evaluation 5 — Significance & contribution to the field

The conceptual framing — *most published cardiometabolic pleiotropy claims rest on `coloc.abf` under identity-LD; how many survive a real-LD re-analysis?* — is exactly the right question to ask in 2026. Genome-wide fine-mapping miscalibration under LD-reference mismatch is documented (Kanai et al. 2022 *Cell Genomics*; Weissbrod et al. 2020 *Nat Genet*; Wallace 2020 *PLoS Genet*), and a curated-locus audit is a sensible vehicle. The pre-registered negative controls (cosmetic, blood-group), the venue ladder (Genome Medicine → AJHG → Bioinformatics), and the candid retraction of evolutionary-medicine and ML-framing overreach from the prior draft are all signs of a researcher operating at high scientific-integrity standards.

**However:** the substantive contribution requires the headline contrast to be quantitatively defensible. As currently positioned:

- The 4.25× claim is built on a non-comparator (Eval 1).
- The Tier-C peak (FTO 0.3099) sits on a fit where the "real LD" was not effectively applied (Eval 3.1).
- The flagship SH2B3 "collapse" is a missing run, not a collapse (Eval 3.4).
- The pathway-enrichment retraction (the most intellectually honest move in the paper) renders the biology section descriptively empty.

What's left is a methodological observation that *real-LD pipelines fail in different ways than identity-LD pipelines do*, supported by a 78.9 % QTL failure rate of disclosed-known cause and a non-converged SuSiE flagship. That's a worthwhile bioRxiv methods note. As a Genome Medicine *Original Research* submission, it will not survive review without the corrections below.

---

## High-quality improvements (3)

1. **Re-derive the headline from the k2d re-fire, then propagate.** The `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` already contains the same-pipeline identity-LD comparator. Replace `N_IDENTITY_LD_NONEMPTY <- 12L` in `fig2_cs_yield.R` with the disk-derived count (`sum(n_CS > 0) = 48` over 95 fits), regenerate Figure 2, recompute the fold-change (~1.05×), and rewrite the abstract / Results / Discussion around the *real* finding: that under matched configuration, identity-LD and real-LD yield similar credible-set counts but **different credible-set composition** (which is what Kanai et al. 2022 actually predicts). Then quantify the *composition* difference (PIP shift, lead-variant overlap, top-PIP rank stability) — that's a publishable result that the data actually supports.

2. **Re-run SH2B3 EUR with L raised to 20 and an explicit non-convergence filter, plus run the canonical trait pairs.** Three concrete actions: (i) re-fit BMI/HTN/stroke at SH2B3 EUR with `L = 20` (Zou et al. 2022 recommend L generously above expected number of effects) and report whether n_CS << L, which is the published non-saturation criterion; (ii) drop or flag non-converged fits in all yield counts (currently they are pooled into 51/96); (iii) execute `coloc.susie` on the canonical BMI–HTN and HTN–stroke pairs that the abstract leans on — until that runs, "absent from manifest" is not an audit conclusion. Document the L-sweep convergence behavior in Supplementary Methods. This rebuilds the flagship narrative on solid posterior support.

3. **Quantify and visualize LD-reference quality alongside the PP.H4 estimates.** Add an `ld_overlap_fraction` column to every PP.H4 reported in Table 1 / Table 3. Drop or asterisk any fit with `ld_overlap_fraction < 0.5` (Benner et al. 2017 calibration threshold), and plot PP.H4 vs `ld_overlap_fraction` to show the **dose–response of LD-reference quality on the inferred coloc signal**. This is the actual scientific question hidden inside the manuscript's data and would convert the paper from "how many published claims survive?" (a categorical answer) to "what LD-reference quality is needed for a coloc.susie PP.H4 to be trustworthy?" (a continuous, quantitative answer the field needs). Pasaniuc & Price 2017 and Kanai et al. 2022 lay the methodological groundwork.

---

## Quick improvements (3)

1. **Purge the ghost numbers and reconcile denominators.** Search-and-destroy any remaining `1,446` / `861` references (the `ID-VS-REF-LD-STRATEGY.md` abstract draft still has them); reconcile `95` (TSV rows) vs `96` (headline denominator) with one paragraph in the Methods naming the missing fit and why; remove the `12 / 96 (12.5 %)` from `fig2_cs_yield.R` line 60 and replace with the disk-derived count. ~30 minutes of work that fixes three reviewer blocking issues.

2. **Move HLA out of the negative-control set, or out of the fallback set — pick one.** The double classification (manuscript L80 vs L102) is internally inconsistent and mathematically deflates the negative-control test. Keep HLA as identity-LD-fallback and remove it from "negative controls"; or keep it as a pre-specified ancestry-stratification control and exclude it from any inference about real-LD performance. Then restate the negative-control N as **distinct loci** (≈10), not rows (224). ~15 minutes.

3. **Add a "data quality" column to Tier-C reporting and recompute the headline.** For each of the 9 Tier-C rows, append `ld_overlap_fraction`, `susie_status`, `n_CS_lt_L`, and `qtl_coloc_status`. The FTO 0.3099 row will surface its `ld_overlap_fraction = 0` problem; readers can then decide whether the highest Tier-C signal is interpretable. This single table change turns a hidden caveat into disclosed data and pre-empts the most likely reviewer objection. ~1 hour, no re-fitting.

---

## References

1. Wang, Sarkar, Carbonetto & Stephens. *J. R. Stat. Soc. B* 82(5):1273–1300 (2020). — SuSiE; L-saturation diagnostics.
2. Zou, Carbonetto, Wang & Stephens. *PLoS Genet* 18:e1010299 (2022). — SuSiE-RSS; convergence and L recommendations.
3. Wallace. *PLoS Genet* 17:e1009440 (2021). — `coloc.susie`; credible-set–level coloc requires reliable posteriors.
4. Wallace. *PLoS Genet* 16:e1008720 (2020). — Prior elicitation for coloc.
5. Kanai *et al.* *Cell Genomics* 2:100210 (2022). — Fine-mapping miscalibration from LD-reference mismatch.
6. Weissbrod *et al.* *Nat Genet* 52:1355–1363 (2020). — Functionally informed fine-mapping; LD-mismatch handling.
7. Benner *et al.* *Bioinformatics* 32:1493–1501 (2016) and *AJHG* 101(4):539–551 (2017). — FINEMAP; LD-reference panel size requirements.
8. Pasaniuc & Price. *Nat Rev Genet* 18:117–127 (2017). — LD-reference panel sizing for summary-statistic fine-mapping.
9. Giambartolomei *et al.* *PLoS Genet* 10:e1004383 (2014). — `coloc.abf`; the method under audit.
10. Hukku, Pividori *et al.* *AJHG* 108:25–35 (2021). — Coloc rigor and pitfalls for cross-trait inference.
11. Foley *et al.* *Nat Commun* 12:764 (2021). — HyPrColoc; multi-trait coloc context.

---

## Bottom line for Carter

This is a fundamentally honest project doing the right *kind* of audit, with a strong reproducibility infrastructure and (impressively) the courage to retract its own previous claims (ML framing, evolutionary-medicine framing, pathway-enrichment headline). But the headline claim is currently inverted by the snapshot's own k2d identity-LD re-fire data, and several supporting claims rest on fits with documented quality problems (LD overlap = 0, SuSiE non-convergence, variant-ID mismatch). Before bioRxiv: regenerate Figure 2 from `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`, re-run SH2B3 with L = 20 and the canonical trait pairs, and add an LD-overlap column to every PP.H4. After that, this becomes a strong, defensible methods-and-audit paper — the question being asked is genuinely worth a Genome Medicine submission.
