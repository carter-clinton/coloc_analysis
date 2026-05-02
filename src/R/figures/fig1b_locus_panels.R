#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# Figure 1B — Regional CS-membership panels at two anchor loci
#
# Purpose
# -------
# Two-panel vertical composite showing credible-set structure under Stage 2
# real-LD SuSiE-RSS fine-mapping at two anchor loci that illustrate the Track A
# identity-vs-real-LD audit narrative:
#
#   Panel 1 (flagship): SH2B3 12q24 — asthma.EUR
#     The canonical SH2B3 identity-LD collapse. At canonical leads rs3184504 /
#     rs10774625, Stage 1 identity-LD coloc reported PP.H4 = 1.00 for the
#     BMI-hypertension and hypertension-stroke trait-pairs; Stage 2 real-LD
#     SuSiE-RSS produced n_cs_a = 0 at those trait pairs (structural collapse
#     precluding the pairwise test, see Stage 2 coloc_summary.tsv). asthma.EUR
#     is the single trait-ancestry at this curated region with a non-empty
#     converged real-LD credible set (1 CS, 140 variants; see
#     results/fine_mapping/finemap_summary.tsv).
#
#   Panel 2 (rescued): FTO 16q12 — bmi.EUR
#     Tier C leader per .planning/STATE.md:293 and manuscript abstract:
#     PP.H4 = 0.3099 at FTO_16q12 EUR for IRX3 / Pancreas (GTEx eQTL). Picked
#     from the 9 Tier C EUR signals (tier_assignments.tsv) by deterministic
#     purity: highest best_qtl_pph4 > 0, converged, non-L-saturated, tie-broken
#     by smallest min_cs_size + highest max_top_pip. Pick provenance block
#     emitted at runtime. bmi.EUR selected over asthma.EUR / t2d.EUR / others
#     at FTO_16q12 because (a) BMI is the canonical FTO phenotype, (b) same
#     PP.H4, (c) cleanest CS structure (10 CS, 7 high-PIP singletons, 1 CS of 5).
#
# Caveats
# -------
#   * Real-LD overlap at FTO_16q12 EUR Stage 2 fit: ld_overlap_fraction = 0
#     (ld_status = "variants_exceed_threshold"). SuSiE effectively fell back
#     toward an identity-like internal structure at this region; we still plot
#     the CS-member variants because the singleton CS structure is
#     interpretable. Limitation surfaced in the Figure 1B caption and in the
#     Discussion's §Limitations subsection.
#   * Identity-LD per-SNP overlay is DEFERRED to a post-k2d-fire /gsd-quick
#     pass (see .planning/quick/260424-k2d-.../ PLAN.md). When identity-LD
#     SuSiE outputs exist under results_identity_ld/, a follow-on pass will
#     overplot identity-LD z-statistics as a second layer. Insertion point
#     marked TODO-K2D below.
#
# Data sources
# ------------
#   results/fine_mapping/susie/asthma.EUR.SH2B3_12q24.json   (SH2B3 flagship CS)
#   results/fine_mapping/susie/bmi.EUR.FTO_16q12.json        (FTO rescued CS)
#   results/qtl_coloc/tier_assignments.tsv                    (Tier C selection)
#   data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz    (SH2B3 regional p-vals)
#   data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz       (FTO regional p-vals)
#   data/reference/magma/NCBI37.3.gene.loc                    (GRCh37 gene track)
#
# Outputs
# -------
#   docs/manuscript/figures/fig1b_locus_panels.pdf  (cairo_pdf, 85 x 160 mm)
#   docs/manuscript/figures/fig1b_locus_panels.png  (600 dpi, same dims)
#
# Render env
# ----------
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
#   R 4.4.2 + ggplot2 4.0.1 + gggenes 0.6.0 + patchwork 1.3.x + ggrepel 0.9.x
#
# Invocation
# ----------
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
#     src/R/figures/fig1b_locus_panels.R
#
# Figure-number provenance: Track A canonical 5-figure roster per
# .planning/amendments/ID-VS-REF-LD-STRATEGY.md §5. Figure 1 Panel B is the anchor-locus
# companion to Figure 1 Panel A (identity-vs-real PP.H4 scatter, deferred to
# post-k2d pass).
#
# Author: Carter K. Clinton | Quick task: 260424-p1b
# ---------------------------------------------------------------------------

suppressPackageStartupMessages({
  library(jsonlite)
  library(readr)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(ggrepel)
  library(gggenes)
  library(patchwork)
  library(scales)
})

# ---- Paths ----------------------------------------------------------------

SH2B3_JSON <- "results/fine_mapping/susie/asthma.EUR.SH2B3_12q24.json"
FTO_JSON   <- "results/fine_mapping/susie/bmi.EUR.FTO_16q12.json"

SH2B3_SS   <- "data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz"
FTO_SS     <- "data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz"

TIER_TSV   <- "results/qtl_coloc/tier_assignments.tsv"
GENE_LOC   <- "data/reference/magma/NCBI37.3.gene.loc"

OUT_DIR    <- "docs/manuscript/figures"
OUT_PDF    <- file.path(OUT_DIR, "fig1b_locus_panels.pdf")
OUT_PNG    <- file.path(OUT_DIR, "fig1b_locus_panels.png")

# ---- Emit Tier C rescued-locus selection provenance -----------------------

emit_rescued_provenance <- function(tier_tsv) {
  tier <- read_tsv(tier_tsv, show_col_types = FALSE)
  tier_c_eur <- tier |> filter(tier == "Tier C", ancestry == "EUR")
  message("[prov] Tier C EUR candidates (n=", nrow(tier_c_eur), "):")
  print(as.data.frame(tier_c_eur[, c("region", "best_qtl_pph4",
                                     "resolving_gene", "resolving_tissue")]))
  message("[prov] Selection criterion: highest best_qtl_pph4 among Tier C EUR",
          " with converged + non-L_saturated SuSiE fit and n_cs > 0;",
          " tie-broken by min_cs_size asc, max_top_pip desc.")
  message("[prov] Pick: FTO_16q12 x bmi.EUR (PP.H4=0.3099 IRX3/Pancreas);",
          " documented in script header.")
}

emit_rescued_provenance(TIER_TSV)

# ---- Gene-track loader ----------------------------------------------------

load_gene_track <- function(chrom, win_start, win_end, pad = 0L) {
  gene_loc <- read_tsv(
    GENE_LOC, show_col_types = FALSE,
    col_names = c("entrez", "chr", "g_start", "g_end", "strand", "symbol"),
    col_types = "cciicc"
  )
  chrom_str <- as.character(chrom)
  gene_loc |>
    filter(chr == chrom_str,
           g_end   > (win_start - pad),
           g_start < (win_end   + pad)) |>
    mutate(forward = strand == "+",
           xmin = pmin(g_start, g_end),
           xmax = pmax(g_start, g_end)) |>
    select(symbol, xmin, xmax, forward, strand)
}

# ---- SuSiE JSON -> tidy per-variant CS-membership frame -------------------

parse_cs_frame <- function(json_path) {
  j <- fromJSON(json_path, simplifyVector = FALSE)
  cs <- j$credible_sets
  if (length(cs) == 0) {
    return(tibble(CHR = character(), POS = integer(),
                  pip = numeric(), cs_label = character()))
  }
  rows <- lapply(names(cs), function(cs_name) {
    variants <- cs[[cs_name]]
    do.call(rbind, lapply(variants, function(v) {
      data.frame(
        CHR = as.character(v$CHR),
        POS = as.integer(v$POS),
        pip = as.numeric(v$pip),
        cs_label = cs_name,
        stringsAsFactors = FALSE
      )
    }))
  })
  as_tibble(do.call(rbind, rows))
}

# ---- Regional sumstats loader (bgzipped TSV) ------------------------------

load_region_sumstats <- function(bgz_path, chrom, start, end) {
  col_spec <- cols(.default = col_character(),
                   CHR = col_character(), POS = col_integer(),
                   BETA = col_double(), SE = col_double(),
                   P = col_double(), N = col_double())
  P_FLOOR <- 1e-300  # GWAS tools emit P=0 beyond double precision; clip for -log10
  NEGLOG10_CAP <- 30 # Y-axis cap; variants with P < 1e-30 marked separately (see build_assoc_panel)
  read_tsv(bgz_path, show_col_types = FALSE, col_types = col_spec) |>
    filter(CHR == as.character(chrom), POS >= start, POS <= end) |>
    filter(is.finite(P), P < 1) |>
    mutate(neglog10P_raw = -log10(pmax(P, P_FLOOR)),
           neglog10P = pmin(neglog10P_raw, NEGLOG10_CAP),
           capped    = neglog10P_raw > NEGLOG10_CAP)
}

# ---- CS colour palette (up to 10 CS + "Non-CS" grey) ----------------------

cs_palette <- function(n_cs) {
  base <- c("#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F",
            "#8491B4", "#91D1C2", "#DC0000", "#7E6148", "#B09C85")
  nm <- c(paste0("CS", seq_len(n_cs)), "Non-CS")
  setNames(c(head(base, n_cs), "#BDBDBD"), nm)
}

# ---- Assoc sub-panel (geom_point, colored by CS) --------------------------

build_assoc_panel <- function(ss, cs_df, region_label, subtitle = NULL,
                              x_range = NULL) {
  merged <- ss |>
    mutate(join_key = paste0(CHR, ":", POS)) |>
    left_join(
      cs_df |> mutate(join_key = paste0(CHR, ":", POS)) |>
        select(join_key, cs_label, pip_susie = pip),
      by = "join_key"
    ) |>
    mutate(cs_label = ifelse(is.na(cs_label), "Non-CS", cs_label))

  cs_levels <- c(sort(unique(cs_df$cs_label)), "Non-CS")
  merged$cs_label <- factor(merged$cs_label, levels = cs_levels)

  n_cs <- length(unique(cs_df$cs_label))
  pal  <- cs_palette(n_cs)

  # Top-PIP variant per CS for labeling; cap label count at 5 largest CS
  # (by pip-sum) to avoid overplotting when many singleton CS exist
  cs_ranks <- cs_df |>
    group_by(cs_label) |>
    summarise(rank_score = sum(pip, na.rm = TRUE), .groups = "drop") |>
    arrange(desc(rank_score))
  labeled_cs <- head(cs_ranks$cs_label, 5)
  top_per_cs <- cs_df |>
    filter(cs_label %in% labeled_cs) |>
    group_by(cs_label) |>
    slice_max(pip, n = 1, with_ties = FALSE) |>
    ungroup() |>
    left_join(ss |> select(CHR, POS, neglog10P, SNP_ID) |>
                mutate(CHR = as.character(CHR)),
              by = c("CHR", "POS"))

  if (is.null(x_range)) x_range <- range(merged$POS)

  p <- ggplot() +
    geom_point(data = filter(merged, cs_label == "Non-CS"),
               aes(x = POS, y = neglog10P),
               colour = pal["Non-CS"], size = 0.4, alpha = 0.4,
               show.legend = FALSE) +
    geom_point(data = filter(merged, cs_label != "Non-CS", !capped),
               aes(x = POS, y = neglog10P, colour = cs_label),
               size = 1.4, alpha = 0.9) +
    geom_point(data = filter(merged, cs_label != "Non-CS", capped),
               aes(x = POS, y = neglog10P, colour = cs_label),
               size = 1.6, alpha = 0.95, shape = 17) +  # filled triangle = y-capped
    geom_text_repel(
      data = top_per_cs,
      aes(x = POS, y = neglog10P, label = SNP_ID, colour = cs_label),
      size = 2.0, min.segment.length = 0, box.padding = 0.4,
      point.padding = 0.1, max.overlaps = Inf, show.legend = FALSE,
      seed = 1, segment.size = 0.2, force = 2, force_pull = 0.5
    ) +
    scale_colour_manual(values = pal, breaks = setdiff(cs_levels, "Non-CS"),
                        name = "Credible set") +
    scale_x_continuous(labels = function(x) paste0(round(x / 1e6, 2), " Mb"),
                       expand = expansion(mult = 0.01)) +
    coord_cartesian(xlim = x_range, clip = "off") +
    labs(title = region_label, subtitle = subtitle, x = NULL,
         y = expression(-log[10] * "(" * italic(P) * ")")) +
    theme_classic(base_size = 8) +
    theme(
      plot.title = element_text(size = 9, face = "bold",
                                margin = margin(b = 1)),
      plot.subtitle = element_text(size = 6.5, colour = "grey25",
                                   lineheight = 1.05,
                                   margin = margin(b = 3)),
      axis.title.y = element_text(size = 7),
      legend.position = "right",
      legend.key.size = unit(2.5, "mm"),
      legend.text = element_text(size = 6.5),
      legend.title = element_text(size = 7),
      legend.margin = margin(0, 0, 0, 0),
      plot.margin = margin(t = 3, r = 4, b = 0, l = 4)
    )

  p
}

# ---- Gene-track sub-panel (gggenes) ---------------------------------------

build_gene_panel <- function(genes, x_range) {
  ggplot(genes,
         aes(xmin = xmin, xmax = xmax, y = 1, forward = forward,
             label = symbol, fill = forward)) +
    geom_gene_arrow(arrowhead_height = unit(3.5, "mm"),
                    arrowhead_width  = unit(1.8, "mm"),
                    arrow_body_height = unit(3, "mm")) +
    geom_gene_label(align = "centre", grow = TRUE,
                    padding.y = unit(0.4, "mm"), min.size = 4.5,
                    fontface = "italic") +
    scale_fill_manual(values = c(`TRUE` = "#546E7A", `FALSE` = "#90A4AE"),
                      guide = "none") +
    scale_x_continuous(labels = function(x) paste0(round(x / 1e6, 2), " Mb"),
                       expand = expansion(mult = 0.01)) +
    coord_cartesian(xlim = x_range, clip = "off") +
    labs(x = "Chromosome position (GRCh37)", y = NULL) +
    theme_classic(base_size = 8) +
    theme(
      axis.title.x = element_text(size = 7),
      axis.text.y  = element_blank(),
      axis.ticks.y = element_blank(),
      axis.line.y  = element_blank(),
      plot.margin  = margin(t = 0, r = 4, b = 3, l = 4)
    )
}

# ---- Build one locus (assoc + gene track) ---------------------------------

build_locus <- function(json_path, ss_path, title, subtitle = NULL) {
  j <- fromJSON(json_path, simplifyVector = FALSE)
  chrom     <- as.character(j$chrom)
  win_start <- as.integer(j$start)
  win_end   <- as.integer(j$end)

  cs    <- parse_cs_frame(json_path)
  ss    <- load_region_sumstats(ss_path, chrom, win_start, win_end)
  genes <- load_gene_track(chrom, win_start, win_end)

  stopifnot(nrow(ss) > 0)
  message(sprintf("[build] %s: region=chr%s:%d-%d  n_variants=%d  n_cs=%d  n_genes=%d n_capped=%d",
                  title, chrom, win_start, win_end, nrow(ss),
                  length(unique(cs$cs_label)), nrow(genes),
                  sum(ss$capped, na.rm = TRUE)))

  x_range <- c(win_start, win_end)
  p_assoc <- build_assoc_panel(ss, cs, title, subtitle, x_range)
  p_genes <- build_gene_panel(genes, x_range)

  # TODO-K2D: once results_identity_ld/fine_mapping/susie/*.json lands,
  # overlay identity-LD z-stats as a second geom_point layer on p_assoc with
  # shape = 4 (cross) for identity-LD + original circles for real-LD.

  list(assoc = p_assoc, genes = p_genes)
}

# ---- Assemble composite ---------------------------------------------------

sh2b3_subtitle <- paste0(
  "Identity-LD Stage 1: PP.H4 = 1.00 at canonical leads rs3184504 / rs10774625 (BMI-HTN, HTN-stroke).\n",
  "Stage 2 real-LD: n_cs_a = 0 at those trait pairs (locus collapse).\n",
  "Shown: asthma x EUR (only non-collapsed real-LD CS at this region)."
)

fto_subtitle <- paste0(
  "Tier C leader: PP.H4 = 0.3099 for IRX3 / Pancreas (GTEx eQTL).\n",
  "Real-LD overlap exceeded threshold (limitation; SuSiE fell back toward\n",
  "identity-like internal structure). Top-5 CS by pip-sum labelled."
)

sh2b3 <- build_locus(
  SH2B3_JSON, SH2B3_SS,
  title = "SH2B3 12q24 (asthma, EUR) - flagship",
  subtitle = sh2b3_subtitle
)

fto <- build_locus(
  FTO_JSON, FTO_SS,
  title = "FTO 16q12 (BMI, EUR) - rescued Tier C",
  subtitle = fto_subtitle
)

composite <- wrap_plots(
  sh2b3$assoc, sh2b3$genes, fto$assoc, fto$genes,
  ncol = 1,
  heights = c(3.5, 0.8, 3.5, 0.8)
) +
  plot_annotation(
    caption = paste0(
      "Figure 1B. Regional CS-membership panels at two anchor loci.\n",
      "Points coloured by SuSiE-RSS credible-set assignment; grey = non-CS. ",
      "Filled triangles mark variants with -log10(P) > 30 (y-capped).\n",
      "GRCh37 coordinates; gene models from MAGMA NCBI37.3.gene.loc. ",
      "Source: results/fine_mapping/susie/ (Stage 2 real-LD).\n",
      "Identity-LD per-SNP overlay deferred to post-k2d-fire revision."
    ),
    theme = theme(plot.caption = element_text(size = 6.5, hjust = 0,
                                              colour = "grey30",
                                              lineheight = 1.15,
                                              margin = margin(t = 4)))
  )

# ---- Render ---------------------------------------------------------------

dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

stopifnot(capabilities("cairo"))

ggsave(OUT_PDF, composite, width = 170, height = 200, units = "mm",
       device = cairo_pdf)
ggsave(OUT_PNG, composite, width = 170, height = 200, units = "mm",
       dpi = 600)

message(sprintf("[render] wrote %s (%s bytes)", OUT_PDF,
                file.info(OUT_PDF)$size))
message(sprintf("[render] wrote %s (%s bytes)", OUT_PNG,
                file.info(OUT_PNG)$size))
message("[render] Figure 1B complete. 2-panel composite.")
