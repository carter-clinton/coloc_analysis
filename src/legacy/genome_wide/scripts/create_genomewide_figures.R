#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(data.table)
})

# Load data
results <- fread("results/analysis/genomewide_coloc_summary.tsv")
results <- results[status == "SUCCESS"]
results[, PP.H4 := as.numeric(PP.H4)]

output_dir <- "results/figures"
dir.create(output_dir, showWarnings=FALSE, recursive=TRUE)

cat("Loaded", nrow(results), "successful results\n")

#------------------------------------------------------------------------------
# Figure 1: H4 Distribution by Ancestry
#------------------------------------------------------------------------------
cat("Creating Figure 1: H4 Distribution\n")

fig1 <- ggplot(results, aes(x=PP.H4, fill=ancestry)) +
  geom_histogram(bins=50, alpha=0.7, position="identity") +
  facet_wrap(~ancestry, ncol=1, scales="free_y") +
  geom_vline(xintercept=c(0.5, 0.8), linetype="dashed", color="red", alpha=0.7) +
  scale_fill_manual(values=c("EUR"="#2166AC", "AFR"="#B2182B")) +
  labs(
    title="Genome-Wide Colocalization: PP.H4 Distribution",
    subtitle=paste0("N = ", nrow(results), " successful tests"),
    x="PP.H4 (Posterior Probability of Shared Causal Variant)",
    y="Count"
  ) +
  theme_bw() +
  theme(legend.position="none", plot.title=element_text(face="bold"))

ggsave(file.path(output_dir, "Fig1_GW_H4_distribution.pdf"), fig1, width=10, height=8)
ggsave(file.path(output_dir, "Fig1_GW_H4_distribution.png"), fig1, width=10, height=8, dpi=300)

#------------------------------------------------------------------------------
# Figure 2: Trait Pair Heatmap
#------------------------------------------------------------------------------
cat("Creating Figure 2: Trait Pair Heatmap\n")

eur_results <- results[ancestry == "EUR"]
trait_summary <- eur_results[, .(
  n_h4_08 = sum(PP.H4 >= 0.8, na.rm=TRUE),
  n_h4_05 = sum(PP.H4 >= 0.5, na.rm=TRUE),
  max_h4 = max(PP.H4, na.rm=TRUE)
), by=.(trait_a, trait_b)]

fig2 <- ggplot(trait_summary, aes(x=trait_a, y=trait_b, fill=n_h4_08)) +
  geom_tile(color="white", linewidth=0.5) +
  geom_text(aes(label=n_h4_08), color="white", size=6, fontface="bold") +
  scale_fill_gradient(low="#DEEBF7", high="#08519C", name="N Signals\n(H4>=0.8)") +
  labs(
    title="High-Confidence Colocalization Signals by Trait Pair (EUR)",
    subtitle="Genome-Wide Analysis",
    x="Trait 1",
    y="Trait 2"
  ) +
  theme_bw() +
  theme(
    axis.text.x=element_text(angle=45, hjust=1, size=12),
    axis.text.y=element_text(size=12),
    plot.title=element_text(face="bold")
  )

ggsave(file.path(output_dir, "Fig2_GW_trait_heatmap.pdf"), fig2, width=9, height=7)
ggsave(file.path(output_dir, "Fig2_GW_trait_heatmap.png"), fig2, width=9, height=7, dpi=300)

#------------------------------------------------------------------------------
# Figure 3: Top 25 Signals Forest Plot
#------------------------------------------------------------------------------
cat("Creating Figure 3: Top Signals\n")

setorder(results, -PP.H4)
top25 <- head(results, 25)
top25[, label := paste0(region, " (", trait_a, "-", trait_b, ")")]
top25[, label := factor(label, levels=rev(label))]

fig3 <- ggplot(top25, aes(x=PP.H4, y=label, color=ancestry)) +
  geom_segment(aes(x=0.8, xend=PP.H4, yend=label), color="gray70", linewidth=0.5) +
  geom_point(size=4, alpha=0.9) +
  geom_vline(xintercept=0.8, linetype="dashed", color="red", alpha=0.6) +
  scale_color_manual(values=c("EUR"="#2166AC", "AFR"="#B2182B")) +
  scale_x_continuous(limits=c(0.75, 1.01), breaks=seq(0.75, 1.0, 0.05)) +
  labs(
    title="Top 25 Genome-Wide Colocalization Signals",
    x="PP.H4",
    y="",
    color="Ancestry"
  ) +
  theme_bw() +
  theme(
    plot.title=element_text(face="bold"),
    axis.text.y=element_text(size=9)
  )

ggsave(file.path(output_dir, "Fig3_GW_top_signals.pdf"), fig3, width=12, height=10)
ggsave(file.path(output_dir, "Fig3_GW_top_signals.png"), fig3, width=12, height=10, dpi=300)

#------------------------------------------------------------------------------
# Figure 4: Manhattan-style Plot
#------------------------------------------------------------------------------
cat("Creating Figure 4: Manhattan Plot\n")

manhattan_data <- copy(eur_results)
manhattan_data[, chr := as.numeric(chr)]
manhattan_data[, pos := (as.numeric(start) + as.numeric(end)) / 2]
manhattan_data <- manhattan_data[!is.na(chr) & !is.na(pos)]
setorder(manhattan_data, chr, pos)

# Create cumulative position
chr_lengths <- manhattan_data[, .(max_pos = max(pos, na.rm=TRUE)), by=chr]
setorder(chr_lengths, chr)
chr_lengths[, cum_length := cumsum(max_pos) - max_pos]

manhattan_data <- merge(manhattan_data, chr_lengths[, .(chr, cum_length)], by="chr")
manhattan_data[, cum_pos := pos + cum_length]

# Axis labels
axis_labels <- manhattan_data[, .(center = mean(cum_pos)), by=chr]

fig4 <- ggplot(manhattan_data, aes(x=cum_pos, y=PP.H4, color=as.factor(chr %% 2))) +
  geom_point(alpha=0.6, size=1.5) +
  geom_hline(yintercept=c(0.5, 0.8), linetype=c("dotted", "dashed"), 
             color=c("blue", "red"), alpha=0.7) +
  scale_color_manual(values=c("#2166AC", "#67A9CF"), guide="none") +
  scale_x_continuous(breaks=axis_labels$center, labels=axis_labels$chr) +
  scale_y_continuous(limits=c(0, 1), breaks=seq(0, 1, 0.2)) +
  labs(
    title="Genome-Wide Colocalization Manhattan Plot (EUR)",
    subtitle="Dashed line: H4=0.8 (high confidence); Dotted line: H4=0.5 (moderate)",
    x="Chromosome",
    y="PP.H4"
  ) +
  theme_bw() +
  theme(
    plot.title=element_text(face="bold"),
    panel.grid.minor=element_blank(),
    axis.text.x=element_text(size=9)
  )

ggsave(file.path(output_dir, "Fig4_GW_manhattan.pdf"), fig4, width=14, height=6)
ggsave(file.path(output_dir, "Fig4_GW_manhattan.png"), fig4, width=14, height=6, dpi=300)

#------------------------------------------------------------------------------
# Summary
#------------------------------------------------------------------------------
cat("\nFigures saved to:", output_dir, "\n")
cat("Files created:\n")
for (f in list.files(output_dir, pattern="\\.(pdf|png)$")) {
  cat(" ", f, "\n")
}
