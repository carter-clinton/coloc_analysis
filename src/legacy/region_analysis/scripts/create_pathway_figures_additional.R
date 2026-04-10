#!/usr/bin/env Rscript
#==============================================================================
# Additional Pathway Enrichment Visualizations (Fig8-10)
#==============================================================================

library(ggplot2)
library(dplyr)
library(tidyr)

project_dir <- "/share/clintonlab/ckclinto/admix_map"
output_dir <- file.path(project_dir, "results/figures")

cat("Creating additional pathway figures (Fig8-10)...\n\n")

#------------------------------------------------------------------------------
# Figure 8: Gene-Trait Colocalization Network (Dot Plot)
#------------------------------------------------------------------------------
cat("Creating Figure 8: Gene-Trait Network...\n")

# Create gene-trait-pathway data
network_data <- data.frame(
  Gene = c("TCF7L2", "TCF7L2", "GCKR", "GCKR", "IRS1", "IRS1", 
           "MC4R", "MC4R", "MC4R", "KCNJ11", "KCNJ11",
           "SH2B3", "SH2B3", "SH2B3", "PPARG", "PPARG",
           "APOE", "APOE", "FTO", "FTO", "NEGR1", "NEGR1", "NEGR1",
           "FADS1", "FADS1", "TMEM18", "TMEM18"),
  Trait = c("BMI", "T2D", "BMI", "T2D", "T2D", "Hypertension",
            "BMI", "T2D", "Hypertension", "T2D", "Hypertension",
            "BMI", "Stroke", "Hypertension", "T2D", "Hypertension",
            "BMI", "Stroke", "BMI", "T2D", "BMI", "T2D", "Asthma",
            "T2D", "Asthma", "BMI", "T2D"),
  H4 = c(1.00, 1.00, 0.999, 0.999, 0.96, 0.96,
         0.97, 0.97, 0.95, 0.97, 0.91,
         0.996, 0.996, 0.96, 0.68, 0.68,
         0.999, 0.95, 0.88, 0.96, 0.91, 0.97, 0.84,
         0.92, 0.85, 0.93, 0.93),
  Pathway = c("Wnt/Insulin", "Wnt/Insulin", "Glucose", "Glucose", "Insulin", "Insulin",
              "Appetite", "Appetite", "Appetite", "Insulin", "Insulin",
              "Inflammation", "Inflammation", "Inflammation", "Insulin", "Insulin",
              "Lipid", "Lipid", "Appetite", "Appetite", "Appetite", "Appetite", "Appetite",
              "Fatty acid", "Fatty acid", "Adipogenesis", "Adipogenesis"),
  stringsAsFactors = FALSE
)

# Order genes by number of trait connections
gene_order <- network_data %>%
  group_by(Gene) %>%
  summarise(n_traits = n()) %>%
  arrange(desc(n_traits)) %>%
  pull(Gene)

network_data$Gene <- factor(network_data$Gene, levels = rev(gene_order))

fig8 <- ggplot(network_data, aes(x = Trait, y = Gene, size = H4, color = Pathway)) +
  geom_point(alpha = 0.8) +
  scale_size_continuous(range = c(3, 10), name = "PP.H4") +
  scale_color_manual(values = c(
    "Wnt/Insulin" = "#E41A1C",
    "Glucose" = "#FF7F00",
    "Insulin" = "#E41A1C",
    "Appetite" = "#984EA3",
    "Inflammation" = "#4DAF4A",
    "Lipid" = "#377EB8",
    "Fatty acid" = "#377EB8",
    "Adipogenesis" = "#F781BF"
  )) +
  labs(
    title = "Gene-Trait Colocalization Network",
    subtitle = "Bubble size = PP.H4, Color = Biological Pathway",
    x = "Trait",
    y = "Gene"
  ) +
  theme_bw() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 11),
    axis.text.y = element_text(size = 10),
    plot.title = element_text(size = 14, face = "bold"),
    legend.position = "right"
  )

ggsave(file.path(output_dir, "Fig8_gene_trait_network.pdf"), fig8, width = 10, height = 8)
ggsave(file.path(output_dir, "Fig8_gene_trait_network.png"), fig8, width = 10, height = 8, dpi = 300)

#------------------------------------------------------------------------------
# Figure 9: Pathway-Trait Connection Heatmap
#------------------------------------------------------------------------------
cat("Creating Figure 9: Pathway-Trait Heatmap...\n")

# Create hub visualization showing how pathways connect traits
hub_data <- data.frame(
  Pathway = c("Insulin signaling", "Insulin signaling", "Insulin signaling",
              "Appetite regulation", "Appetite regulation", "Appetite regulation",
              "Inflammation", "Inflammation", "Inflammation",
              "Lipid transport", "Lipid transport", "Lipid transport",
              "Glucose metabolism", "Glucose metabolism"),
  Trait = c("T2D", "Hypertension", "BMI",
            "BMI", "T2D", "Hypertension",
            "BMI", "Stroke", "Hypertension",
            "BMI", "Stroke", "T2D",
            "BMI", "T2D"),
  N_Genes = c(4, 3, 2, 4, 3, 2, 1, 1, 1, 2, 2, 1, 2, 2),
  stringsAsFactors = FALSE
)

fig9 <- ggplot(hub_data, aes(x = Trait, y = Pathway, fill = N_Genes)) +
  geom_tile(color = "white", size = 1) +
  geom_text(aes(label = N_Genes), color = "white", size = 6, fontface = "bold") +
  scale_fill_gradient(low = "#FEE0D2", high = "#DE2D26", name = "N Genes") +
  labs(
    title = "Pathway-Trait Connections",
    subtitle = "Number of pleiotropic genes linking each pathway to each trait",
    x = "Disease Trait",
    y = "Biological Pathway"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    axis.text = element_text(size = 11),
    axis.text.x = element_text(angle = 45, hjust = 1),
    panel.grid = element_blank()
  )

ggsave(file.path(output_dir, "Fig9_pathway_trait_heatmap.pdf"), fig9, width = 8, height = 6)
ggsave(file.path(output_dir, "Fig9_pathway_trait_heatmap.png"), fig9, width = 8, height = 6, dpi = 300)

#------------------------------------------------------------------------------
# Figure 10: Specific Pathway Breakdown (Horizontal Bar Chart)
#------------------------------------------------------------------------------
cat("Creating Figure 10: Specific Pathways Breakdown...\n")

specific_pathways <- data.frame(
  Pathway = c("Insulin signaling", "Appetite regulation", "Insulin secretion",
              "Lipid transport", "Fatty acid metabolism", "Inflammation",
              "Glucose metabolism", "Adipogenesis", "Wnt signaling"),
  N_Genes = c(4, 4, 2, 2, 2, 1, 1, 1, 1),
  Category = c("Metabolic", "Metabolic", "Metabolic", "Lipid", "Lipid", "Immune", 
               "Metabolic", "Metabolic", "Metabolic"),
  stringsAsFactors = FALSE
)

specific_pathways <- specific_pathways %>%
  arrange(desc(N_Genes)) %>%
  mutate(Pathway = factor(Pathway, levels = rev(Pathway)))

fig10 <- ggplot(specific_pathways, aes(x = N_Genes, y = Pathway, fill = Category)) +
  geom_bar(stat = "identity", width = 0.7) +
  geom_text(aes(label = N_Genes), hjust = -0.3, size = 4) +
  scale_fill_manual(values = c(
    "Metabolic" = "#E41A1C",
    "Lipid" = "#377EB8",
    "Immune" = "#4DAF4A"
  )) +
  labs(
    title = "Specific Pathway Enrichment",
    subtitle = "Number of pleiotropic genes per biological pathway",
    x = "Number of Genes",
    y = "Pathway"
  ) +
  theme_bw() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    axis.text.y = element_text(size = 10)
  ) +
  xlim(0, 5)

ggsave(file.path(output_dir, "Fig10_specific_pathways_breakdown.pdf"), fig10, width = 9, height = 6)
ggsave(file.path(output_dir, "Fig10_specific_pathways_breakdown.png"), fig10, width = 9, height = 6, dpi = 300)

cat("\nAdditional pathway figures created successfully:\n")
cat("  - Fig8_gene_trait_network.pdf/png\n")
cat("  - Fig9_pathway_trait_heatmap.pdf/png\n")
cat("  - Fig10_specific_pathways_breakdown.pdf/png\n")
cat("\nTotal pathway figures: Fig6, Fig7, Fig8, Fig9, Fig10 (10 files)\n")
