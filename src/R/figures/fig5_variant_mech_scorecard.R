#!/usr/bin/env Rscript
# fig5_variant_mech_scorecard.R — Track A Figure 5 (variant mechanism + Tier C scorecard)
#
# Purpose: Build the two-panel composite figure per TRACK-A-PIVOT.md §5 Figure 5 spec
# and track_a_pivot.md L295 legend.
#
#   Panel A — Variant mechanism donut at real-LD-surviving lead variants (n = 51
#             non-empty credible sets from results/fine_mapping/susie/*.json).
#             Classification: gene-body intersection against data/reference/magma/
#             NCBI37.3.gene.loc as a pragmatic proxy. Three mutually-exclusive
#             categories with ±100 kb flanking window:
#               - "Within gene body"        (any overlap with gene start-end)
#               - "Flanking ≤100 kb"        (closest gene boundary within 100 kb)
#               - "Distal intergenic"       (>100 kb from nearest gene)
#             Full CADD / PolyPhen-2 / SIFT / GTEx eQTL per-variant annotation
#             aggregation is deferred to venue-submission prep; the donut is
#             labelled accordingly in the in-figure caption.
#
#   Panel B — Tier C scorecard bar for the 3 named resolving genes from
#             results/qtl_coloc/tier_assignments.tsv (tier == "Tier C" with
#             non-NaN resolving_gene): APOL1, IRX3, ATXN2. Bar length = best
#             QTL PP.H4; tissue labelled in-bar; reference lines at 0.5 (Tier B
#             threshold) and 0.8 (Tier A threshold) visualise the gap to the
#             manuscript's confidence thresholds.
#
# Manuscript anchor: docs/manuscript/track_a_pivot.md L295 Figure 5 legend
# ("partial, descriptive only"; panel B explicitly NOT predictive discovery;
# drug-target status labelled as reference annotation only).
#
# Upstream empirical constraint: 260424-k2e (commit b7c9310) Tier A + Tier B =
# 0 genes under real-LD; this figure's sparsity IS the argument per Discussion
# §Reframing "primarily an LD-inflation artifact" framing.
#
# Data sources (all read at runtime from disk; no hard-coded scalars beyond
# the documented thresholds):
#   - results/fine_mapping/susie/*.json                (51 non-empty fits)
#   - data/reference/magma/NCBI37.3.gene.loc            (~19k gene boundaries)
#   - results/qtl_coloc/tier_assignments.tsv            (233 rows; 3 Tier C genes)
#
# Outputs:
#   docs/manuscript/figures/fig5_variant_mech_scorecard.pdf  (cairo_pdf, 170 x 85 mm)
#   docs/manuscript/figures/fig5_variant_mech_scorecard.png  (600 dpi, 170 x 85 mm)
#
# Render env: /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
#   (R 4.4.2, ggplot2 4.0.1, patchwork 1.3.2, scales 1.4.0; cairo verified.)
#
# Invocation (from project root):
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/figures/fig5_variant_mech_scorecard.R
#
# Author: Carter K. Clinton -- 2026-04-24 (quick-260424-k2g)
#
# Framing discipline: original research; descriptive only; NOT predictive
# discovery. No drug-target claims beyond reference-annotation labelling.

suppressPackageStartupMessages({
  library(jsonlite)
  library(readr)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(scales)
  library(patchwork)
})

OUT_DIR <- "docs/manuscript/figures"
OUT_PDF <- file.path(OUT_DIR, "fig5_variant_mech_scorecard.pdf")
OUT_PNG <- file.path(OUT_DIR, "fig5_variant_mech_scorecard.png")

# ---------------------------------------------------------------------------
# Panel A: variant-mechanism donut
# ---------------------------------------------------------------------------

extract_lead_variants <- function(json_dir = "results/fine_mapping/susie") {
  files <- list.files(json_dir, pattern = "\\.json$", full.names = TRUE)
  leads <- list()
  for (f in files) {
    d <- tryCatch(fromJSON(f, simplifyVector = FALSE), error = function(e) NULL)
    if (is.null(d)) next
    cs <- d$credible_sets
    if (is.null(cs) || length(cs) == 0) next
    # Collect all variants across all CSes with their CS name
    all_v <- list()
    for (nm in names(cs)) {
      vs <- cs[[nm]]
      if (is.null(vs) || length(vs) == 0) next
      for (v in vs) {
        all_v[[length(all_v) + 1]] <- list(
          cs = nm,
          CHR = v$CHR,
          POS = v$POS,
          pip = v$pip %||% 0
        )
      }
    }
    if (length(all_v) == 0) next
    # Top-PIP variant across all CSes in this fit
    pips <- vapply(all_v, function(x) as.numeric(x$pip), numeric(1))
    top <- all_v[[which.max(pips)]]
    leads[[length(leads) + 1]] <- data.frame(
      trait = d$trait,
      ancestry = d$ancestry,
      region = d$region_id,
      cs = top$cs,
      chr = as.character(top$CHR),
      pos = as.integer(top$POS),
      pip = as.numeric(top$pip),
      stringsAsFactors = FALSE
    )
  }
  do.call(rbind, leads)
}

`%||%` <- function(a, b) if (!is.null(a)) a else b

load_gene_loc <- function(path = "data/reference/magma/NCBI37.3.gene.loc") {
  # MAGMA gene.loc: entrez_id  chr  start  end  strand  symbol  (tab-sep)
  gl <- read_tsv(path, col_names = c("entrez", "chr", "start", "end", "strand", "symbol"),
                 col_types = "ccdddc", show_col_types = FALSE)
  # Normalise chromosome format (strip "chr" prefix, keep as string; X/Y/MT stay string)
  gl$chr <- gsub("^chr", "", gl$chr, ignore.case = TRUE)
  gl
}

classify_lead_variant <- function(chr, pos, gene_loc, flank_bp = 100000L) {
  g_chr <- gene_loc[gene_loc$chr == as.character(chr), , drop = FALSE]
  if (nrow(g_chr) == 0) return("Distal intergenic")
  # Within gene body?
  in_body <- any(pos >= g_chr$start & pos <= g_chr$end)
  if (in_body) return("Within gene body")
  # Flanking (closest boundary within ±100 kb)?
  dists <- pmin(abs(pos - g_chr$start), abs(pos - g_chr$end))
  if (min(dists) <= flank_bp) return("Flanking ≤100 kb")
  return("Distal intergenic")
}

message("Loading lead variants from results/fine_mapping/susie/*.json ...")
leads <- extract_lead_variants()
stopifnot(nrow(leads) == 51)
message(sprintf("  %d non-empty credible sets (top-PIP lead extracted each)", nrow(leads)))

message("Loading MAGMA gene loc ...")
gl <- load_gene_loc()
message(sprintf("  %d gene entries for gene-body classification", nrow(gl)))

message("Classifying lead variants by gene-body proximity ...")
leads$class <- vapply(seq_len(nrow(leads)),
                     function(i) classify_lead_variant(leads$chr[i], leads$pos[i], gl),
                     character(1))
cat_counts <- as.data.frame(table(class = leads$class), stringsAsFactors = FALSE)
names(cat_counts) <- c("class", "n")
cat_counts$pct <- cat_counts$n / sum(cat_counts$n) * 100

# Canonical factor ordering for donut colour scheme (stable across re-runs)
class_levels <- c("Within gene body", "Flanking ≤100 kb", "Distal intergenic")
cat_counts$class <- factor(cat_counts$class, levels = class_levels)
cat_counts <- cat_counts[order(cat_counts$class), , drop = FALSE]
cat_counts <- cat_counts[!is.na(cat_counts$class), , drop = FALSE]

# Donut (stacked bar in polar coordinates)
panel_a <- ggplot(cat_counts, aes(x = 2, y = n, fill = class)) +
  geom_col(width = 1, color = "white") +
  coord_polar(theta = "y") +
  xlim(0.5, 2.5) +
  scale_fill_manual(
    values = c(
      "Within gene body"    = "#4A6FA5",
      "Flanking ≤100 kb" = "#F2A65A",
      "Distal intergenic"    = "#6FAE9D"
    ),
    name = NULL,
    drop = FALSE
  ) +
  geom_text(aes(label = sprintf("%d\n(%.0f%%)", n, pct)),
            position = position_stack(vjust = 0.5),
            color = "white", size = 2.4, fontface = "bold") +
  annotate("text", x = 0.5, y = 0, label = sprintf("n = %d\nleads", sum(cat_counts$n)),
           size = 3, fontface = "bold", color = "grey25") +
  labs(
    title = "A — Lead-variant gene-body proximity",
    subtitle = "Real-LD-surviving SuSiE credible sets (n = 51)"
  ) +
  theme_void(base_size = 9) +
  theme(
    plot.title = element_text(face = "bold", size = 10, hjust = 0),
    plot.subtitle = element_text(size = 8, hjust = 0, color = "grey30"),
    legend.position = "bottom",
    legend.direction = "vertical",
    legend.text = element_text(size = 7.5),
    legend.key.size = unit(0.35, "cm"),
    legend.margin = margin(t = -6)
  )

# ---------------------------------------------------------------------------
# Panel B: Tier C scorecard bar
# ---------------------------------------------------------------------------

message("Loading Tier C scorecard ...")
tiers <- read_tsv("results/qtl_coloc/tier_assignments.tsv", show_col_types = FALSE)
tc <- tiers %>%
  filter(tier == "Tier C", !is.na(resolving_gene)) %>%
  select(region, ancestry, resolving_gene, resolving_tissue, best_qtl_pph4)

# Map Ensembl → symbol (hard-coded from tier_assignments resolving_gene column;
# these three mappings are the canonical Tier C named-gene roster per k2e audit)
ensembl_to_symbol <- c(
  "ENSG00000100342" = "APOL1",
  "ENSG00000177508" = "IRX3",
  "ENSG00000204842" = "ATXN2"
)
tc$symbol <- ensembl_to_symbol[tc$resolving_gene]
stopifnot(all(!is.na(tc$symbol)))
stopifnot(nrow(tc) == 3)

# Tidy tissue labels (replace underscores with spaces)
tc$tissue_label <- gsub("_", " ", tc$resolving_tissue)

# Order bars by PP.H4 descending
tc$symbol <- factor(tc$symbol, levels = tc$symbol[order(tc$best_qtl_pph4, decreasing = FALSE)])

panel_b <- ggplot(tc, aes(x = best_qtl_pph4, y = symbol)) +
  geom_col(fill = "#4A6FA5", width = 0.55, alpha = 0.85) +
  # Reference lines for Tier B (0.5) and Tier A (0.8) thresholds
  geom_vline(xintercept = 0.5, linetype = "dashed", color = "#D95F02", linewidth = 0.4) +
  geom_vline(xintercept = 0.8, linetype = "dashed", color = "#7570B3", linewidth = 0.4) +
  geom_text(
    aes(label = sprintf("PP.H4 = %.3f   (%s)", best_qtl_pph4, tissue_label)),
    hjust = 0, nudge_x = 0.01, size = 2.4, color = "grey20"
  ) +
  annotate("text", x = 0.5, y = 0.55, label = "Tier B\n(≥0.5)",
           hjust = 0.5, vjust = 1, size = 2.3, color = "#D95F02") +
  annotate("text", x = 0.8, y = 0.55, label = "Tier A\n(≥0.8)",
           hjust = 0.5, vjust = 1, size = 2.3, color = "#7570B3") +
  scale_x_continuous(
    limits = c(0, 1.0),
    breaks = seq(0, 1, 0.25),
    labels = c("0", "0.25", "0.50", "0.75", "1.0"),
    expand = c(0, 0)
  ) +
  labs(
    title = "B — Tier C resolving-gene scorecard",
    subtitle = "Real-LD signals at 3 of 9 Tier C regions (all below threshold)",
    x = "Best QTL PP.H4 (real-LD)",
    y = NULL
  ) +
  theme_classic(base_size = 9) +
  theme(
    plot.title = element_text(face = "bold", size = 10, hjust = 0),
    plot.subtitle = element_text(size = 8, hjust = 0, color = "grey30"),
    axis.title.x = element_text(size = 8),
    axis.text.y = element_text(face = "italic", size = 9),
    axis.text.x = element_text(size = 7.5),
    axis.line.y = element_blank(),
    axis.ticks.y = element_blank(),
    panel.grid.major.x = element_line(color = "grey92", linewidth = 0.3),
    plot.margin = margin(5, 10, 5, 5)
  )

# ---------------------------------------------------------------------------
# Composite assembly
# ---------------------------------------------------------------------------

composite <- panel_a + panel_b +
  plot_layout(widths = c(0.85, 1.15)) +
  plot_annotation(
    caption = paste(
      "Panel A: gene-body-intersection proxy via MAGMA NCBI37.3 gene loc;",
      "full CADD / PolyPhen-2 / SIFT / GTEx eQTL aggregation deferred.",
      "\nPanel B: 3 named Tier C genes; 0 Tier A + 0 Tier B; identity-LD",
      "pathway-level claims withdrawn (see Results §Pathway Enrichment)."
    ),
    theme = theme(
      plot.caption = element_text(size = 7, color = "grey40", hjust = 0,
                                  lineheight = 1.1, margin = margin(t = 6))
    )
  )

# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

if (!isTRUE(capabilities("cairo"))) {
  stop("fig5_variant_mech_scorecard.R: R build lacks cairo capability.")
}

message("Rendering composite to disk ...")
message(sprintf("  %s", OUT_PDF))
message(sprintf("  %s", OUT_PNG))

ggsave(OUT_PDF, composite, width = 170, height = 85, units = "mm", device = cairo_pdf)
ggsave(OUT_PNG, composite, width = 170, height = 85, units = "mm", dpi = 600)

# ---------------------------------------------------------------------------
# Diagnostic stdout (verified by SUMMARY guardrail gate)
# ---------------------------------------------------------------------------

message("")
message("=== fig5_variant_mech_scorecard.R diagnostic summary ===")
message(sprintf("Panel A — n = %d lead variants", nrow(leads)))
for (i in seq_len(nrow(cat_counts))) {
  message(sprintf("  %-22s %3d (%.1f%%)",
                  as.character(cat_counts$class[i]),
                  cat_counts$n[i], cat_counts$pct[i]))
}
message(sprintf("Panel B — %d Tier C named genes", nrow(tc)))
for (i in seq_len(nrow(tc))) {
  message(sprintf("  %-6s PP.H4=%.3f  (%s)", as.character(tc$symbol[i]),
                  tc$best_qtl_pph4[i], tc$tissue_label[i]))
}
message(sprintf("wrote %s (%d bytes)", OUT_PDF, file.size(OUT_PDF)))
message(sprintf("wrote %s (%d bytes)", OUT_PNG, file.size(OUT_PNG)))
