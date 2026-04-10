#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
  library(gridExtra)
})

counts_path <- "results/analysis/coloc_h4_traitpair_counts.tsv"
top_hits_path <- "results/analysis/coloc_top_hits_table.tsv"

if (!file.exists(counts_path)) {
  stop("Missing counts table: ", counts_path)
}
if (!file.exists(top_hits_path)) {
  stop("Missing top hits table: ", top_hits_path)
}

counts <- fread(counts_path)
if (nrow(counts) == 0) {
  stop("Counts table is empty: ", counts_path)
}
counts[, trait_pair := gsub("__", " vs ", trait_pair)]
counts[, set := factor(set, levels = c("clean_h4", "candidate_h4"))]
counts[, total_pair := ave(n_loci, set, trait_pair, FUN = sum)]

p_counts <- ggplot(
  counts,
  aes(x = reorder(trait_pair, total_pair), y = n_loci, fill = ancestry)
) +
  geom_col(position = position_dodge(width = 0.8)) +
  coord_flip() +
  facet_wrap(~ set, scales = "free_y") +
  labs(
    title = "H4 shared-causal loci by trait pair",
    x = NULL,
    y = "Distinct loci (PP.H4 >= 0.8)",
    fill = "Ancestry"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    strip.text = element_text(face = "bold"),
    legend.position = "top"
  )

top_hits <- fread(top_hits_path)
if (nrow(top_hits) == 0) {
  stop("Top hits table is empty: ", top_hits_path)
}
top_hits <- top_hits[order(-max_pp_h4)]
top_hits <- top_hits[1:min(12, .N)]
top_hits[, trait_pair := gsub("__", " vs ", trait_pair)]

table_cols <- c("base_region", "trait_pair", "eur_PP.H4", "afr_PP.H4", "ancestries_present")
table_cols <- table_cols[table_cols %in% names(top_hits)]
table_df <- as.data.frame(top_hits[, ..table_cols])

tbl <- tableGrob(table_df, rows = NULL, theme = ttheme_minimal(base_size = 9))

out_dir <- "results/plots"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

png_path <- file.path(out_dir, "coloc_h4_summary.png")
pdf_path <- file.path(out_dir, "coloc_h4_summary.pdf")

png(png_path, width = 1400, height = 1000, res = 120)
grid.arrange(p_counts, tbl, ncol = 1, heights = c(2, 1))
dev.off()

pdf(pdf_path, width = 11, height = 8.5)
grid.arrange(p_counts, tbl, ncol = 1, heights = c(2, 1))
dev.off()
