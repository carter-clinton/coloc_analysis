#!/usr/bin/env Rscript
# Pathway Network Visualization

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
})

project_dir <- "/share/clintonlab/ckclinto/admix_map"
pathway_dir <- file.path(project_dir, "results/pathway_analysis")
output_dir <- file.path(project_dir, "results/figures")

cat("Creating pathway network visualizations...\n\n")

#==============================================================================
# Figure 6: Pathway Enrichment Bar Chart
#==============================================================================
cat("Creating Figure 6: Pathway Enrichment...\n")

# Read pathway summary
pathways <- read.delim(file.path(pathway_dir, "gene_pathway_annotations.tsv"))

# Count genes per category
pathway_counts <- pathways %>%
  group_by(Category) %>%
  summarise(n_genes = n()) %>%
  arrange(desc(n_genes)) %>%
  mutate(Category = factor(Category, levels = rev(Category)))

fig6 <- ggplot(pathway_counts, aes(x = Category, y = n_genes)) +
  geom_bar(stat = "identity", fill = "#2166AC", alpha = 0.8) +
  geom_text(aes(label = n_genes), hjust = -0.3, size = 4) +
  coord_flip() +
  labs(
    title = "Pathway Enrichment of Pleiotropic Genes",
    x = "Pathway Category",
    y = "Number of Genes"
  ) +
  theme_bw() +
  theme(
    panel.grid.major.y = element_blank(),
    plot.title = element_text(face = "bold")
  ) +
  scale_y_continuous(limits = c(0, max(pathway_counts$n_genes) + 2))

ggsave(file.path(output_dir, "Fig6_pathway_enrichment.pdf"), fig6, width = 8, height = 5)
ggsave(file.path(output_dir, "Fig6_pathway_enrichment.png"), fig6, width = 8, height = 5, dpi = 300)

#==============================================================================
# Figure 7: Specific Pathway Bar Chart
#==============================================================================
cat("Creating Figure 7: Specific Pathways...\n")

specific_pathways <- pathways %>%
  group_by(Pathway, Category) %>%
  summarise(n_genes = n(), .groups = "drop") %>%
  arrange(desc(n_genes)) %>%
  head(10) %>%
  mutate(Pathway = factor(Pathway, levels = rev(Pathway)))

fig7 <- ggplot(specific_pathways, aes(x = Pathway, y = n_genes, fill = Category)) +
  geom_bar(stat = "identity", alpha = 0.8) +
  geom_text(aes(label = n_genes), hjust = -0.3, size = 3.5) +
  coord_flip() +
  scale_fill_manual(values = c(
    "Metabolic" = "#2166AC",
    "Lipid" = "#B2182B",
    "Immune" = "#1B7837",
    "Cardiovascular" = "#E08214",
    "Cellular" = "#8073AC"
  )) +
  labs(
    title = "Top 10 Specific Pathways",
    x = "Pathway",
    y = "Number of Genes",
    fill = "Category"
  ) +
  theme_bw() +
  theme(
    panel.grid.major.y = element_blank(),
    plot.title = element_text(face = "bold")
  ) +
  scale_y_continuous(limits = c(0, max(specific_pathways$n_genes) + 1))

ggsave(file.path(output_dir, "Fig7_specific_pathways.pdf"), fig7, width = 9, height = 6)
ggsave(file.path(output_dir, "Fig7_specific_pathways.png"), fig7, width = 9, height = 6, dpi = 300)

cat("\nPathway figures saved to:", output_dir, "\n")
cat("\nGenerated files:\n")
list.files(output_dir, pattern = "Fig[67].*\\.(pdf|png)$")
