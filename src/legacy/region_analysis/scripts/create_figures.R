#!/usr/bin/env Rscript
# Publication figures for colocalization analysis

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tidyr)
})

project_dir <- "/share/clintonlab/ckclinto/admix_map"
output_dir <- file.path(project_dir, "results/figures")
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

cat("Creating publication figures...\n\n")

# Load data
coloc <- read.delim(file.path(project_dir, "results/multitrait/coloc_summary.tsv"))
locus_comp <- read.delim(file.path(project_dir, "results/analysis/locus_comparison.tsv"))

#==============================================================================
# Figure 1: H4 Distribution by Ancestry
#==============================================================================
cat("Creating Figure 1: H4 Distribution...\n")

fig1 <- coloc %>%
  filter(!is.na(PP.H4)) %>%
  ggplot(aes(x = PP.H4, fill = ancestry)) +
  geom_histogram(bins = 50, alpha = 0.7, position = "identity") +
  facet_wrap(~ancestry, ncol = 1, scales = "free_y") +
  geom_vline(xintercept = c(0.5, 0.8), linetype = "dashed", color = "red") +
  scale_fill_manual(values = c("EUR" = "#2166AC", "AFR" = "#B2182B")) +
  labs(
    title = "Distribution of Colocalization Posterior Probabilities",
    x = "PP.H4 (Shared Causal Variant)",
    y = "Count",
    fill = "Ancestry"
  ) +
  theme_bw() +
  theme(legend.position = "none")

ggsave(file.path(output_dir, "Fig1_H4_distribution.pdf"), fig1, width = 8, height = 6)
ggsave(file.path(output_dir, "Fig1_H4_distribution.png"), fig1, width = 8, height = 6, dpi = 300)

#==============================================================================
# Figure 2: Cross-Ancestry Comparison
#==============================================================================
cat("Creating Figure 2: Cross-Ancestry Comparison...\n")

fig2_data <- locus_comp %>%
  filter(!is.na(eur_h4) & !is.na(afr_h4) & eur_h4 > 0 & afr_h4 > 0) %>%
  mutate(
    gene = sub("_.*", "", region),
    concordance_color = case_when(
      concordance == "Strong" ~ "Strong",
      concordance == "Moderate" ~ "Moderate",
      TRUE ~ "Discordant"
    )
  )

fig2 <- ggplot(fig2_data, aes(x = eur_h4, y = afr_h4, color = concordance_color)) +
  geom_point(size = 3, alpha = 0.7) +
  geom_hline(yintercept = c(0.05, 0.1), linetype = "dashed", alpha = 0.5) +
  geom_vline(xintercept = c(0.5, 0.8), linetype = "dashed", alpha = 0.5) +
  geom_text(
    data = fig2_data %>% filter(concordance %in% c("Strong", "Moderate")),
    aes(label = gene),
    hjust = -0.2, vjust = 0.5, size = 3
  ) +
  scale_color_manual(values = c(
    "Strong" = "#1B7837",
    "Moderate" = "#7FBC41",
    "Discordant" = "#969696"
  )) +
  labs(
    title = "Cross-Ancestry Colocalization Concordance",
    x = "EUR PP.H4",
    y = "AFR PP.H4",
    color = "Concordance"
  ) +
  theme_bw() +
  coord_cartesian(xlim = c(0, 1), ylim = c(0, 0.2))

ggsave(file.path(output_dir, "Fig2_cross_ancestry.pdf"), fig2, width = 8, height = 6)
ggsave(file.path(output_dir, "Fig2_cross_ancestry.png"), fig2, width = 8, height = 6, dpi = 300)

#==============================================================================
# Figure 3: Trait Pair Heatmap
#==============================================================================
cat("Creating Figure 3: Trait Pair Heatmap...\n")

trait_summary <- coloc %>%
  filter(ancestry == "EUR" & !is.na(PP.H4)) %>%
  group_by(trait_a, trait_b) %>%
  summarise(
    n_h4_08 = sum(PP.H4 >= 0.8),
    n_h4_05 = sum(PP.H4 >= 0.5),
    max_h4 = max(PP.H4),
    .groups = "drop"
  )

fig3 <- trait_summary %>%
  ggplot(aes(x = trait_a, y = trait_b, fill = n_h4_08)) +
  geom_tile(color = "white", size = 0.5) +
  geom_text(aes(label = n_h4_08), color = "white", size = 5, fontface = "bold") +
  scale_fill_gradient(low = "#DEEBF7", high = "#08519C", breaks = c(0, 5, 10, 15)) +
  labs(
    title = "High-Confidence Colocalization Signals (EUR, H4≥0.8)",
    x = "Trait 1",
    y = "Trait 2",
    fill = "N Signals"
  ) +
  theme_bw() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    panel.grid = element_blank()
  )

ggsave(file.path(output_dir, "Fig3_trait_heatmap.pdf"), fig3, width = 7, height = 6)
ggsave(file.path(output_dir, "Fig3_trait_heatmap.png"), fig3, width = 7, height = 6, dpi = 300)

#==============================================================================
# Figure 4: Top Signals Forest Plot Style
#==============================================================================
cat("Creating Figure 4: Top Signals Forest Plot...\n")

top_signals <- coloc %>%
  filter(PP.H4 >= 0.8) %>%
  mutate(gene = sub("_.*", "", region)) %>%
  arrange(desc(PP.H4)) %>%
  head(20) %>%
  mutate(
    label = paste0(gene, " (", trait_a, "-", trait_b, ")"),
    label = factor(label, levels = rev(label))
  )

fig4 <- ggplot(top_signals, aes(x = PP.H4, y = label)) +
  geom_segment(aes(x = 0.8, xend = PP.H4, yend = label), color = "gray70") +
  geom_point(aes(color = ancestry), size = 4) +
  geom_vline(xintercept = 0.8, linetype = "dashed", color = "red", alpha = 0.5) +
  scale_color_manual(values = c("EUR" = "#2166AC", "AFR" = "#B2182B")) +
  scale_x_continuous(limits = c(0.75, 1.01), breaks = seq(0.8, 1.0, 0.05)) +
  labs(
    title = "Top 20 Colocalization Signals",
    x = "PP.H4",
    y = "",
    color = "Ancestry"
  ) +
  theme_bw() +
  theme(
    axis.text.y = element_text(size = 9),
    panel.grid.major.y = element_line(color = "gray90")
  )

ggsave(file.path(output_dir, "Fig4_top_signals.pdf"), fig4, width = 10, height = 8)
ggsave(file.path(output_dir, "Fig4_top_signals.png"), fig4, width = 10, height = 8, dpi = 300)

#==============================================================================
# Figure 5: Pleiotropic Loci Bar Chart
#==============================================================================
cat("Creating Figure 5: Pleiotropic Loci...\n")

pleio <- read.delim(file.path(project_dir, "results/analysis/pleiotropic_loci.tsv"))

if (nrow(pleio) > 0) {
  pleio_plot <- pleio %>%
    mutate(
      gene = sub("_.*", "", region),
      total_pairs = eur_pairs + afr_pairs
    ) %>%
    arrange(desc(total_pairs)) %>%
    head(15) %>%
    mutate(gene = factor(gene, levels = rev(gene)))
  
  fig5 <- ggplot(pleio_plot, aes(x = gene, y = total_pairs)) +
    geom_bar(stat = "identity", fill = "#2166AC", alpha = 0.8) +
    geom_text(aes(label = total_pairs), hjust = -0.2, size = 3.5) +
    coord_flip() +
    labs(
      title = "Pleiotropic Loci (≥2 Trait Pairs with H4≥0.1)",
      x = "Gene/Locus",
      y = "Number of Trait Pairs"
    ) +
    theme_bw() +
    theme(panel.grid.major.y = element_blank())
  
  ggsave(file.path(output_dir, "Fig5_pleiotropic_loci.pdf"), fig5, width = 8, height = 6)
  ggsave(file.path(output_dir, "Fig5_pleiotropic_loci.png"), fig5, width = 8, height = 6, dpi = 300)
}

cat("\nFigures saved to:", output_dir, "\n")
cat("\nGenerated files:\n")
list.files(output_dir, pattern = "\\.(pdf|png)$")
