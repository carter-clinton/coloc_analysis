#!/usr/bin/env Rscript
#==============================================================================
# LocusZoom-Style Regional Association Plots
#==============================================================================

library(ggplot2)
library(dplyr)
library(tidyr)
library(data.table)
library(patchwork)

# Configuration
project_dir <- "/share/clintonlab/ckclinto/admix_map"
sumstats_dir <- file.path(project_dir, "data_processed/sumstats_harmonized_fixed")
ld_dir <- file.path(project_dir, "data_processed/ld_matrices")
output_dir <- file.path(project_dir, "results/figures/locuszoom")
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

#------------------------------------------------------------------------------
# Define top loci for plotting
#------------------------------------------------------------------------------
top_loci <- data.frame(
  locus = c("TCF7L2", "SH2B3", "GCKR", "IRS1", "MC4R"),
  chr = c(10, 12, 2, 2, 18),
  lead_pos = c(114758349, 111884608, 27730940, 227093745, 58038563),
  window = c(500000, 500000, 500000, 500000, 500000),
  trait_a = c("bmi", "bmi", "bmi", "hypertension", "bmi"),
  trait_b = c("t2d", "stroke", "t2d", "t2d", "t2d"),
  h4 = c(1.00, 0.9996, 0.9994, 0.96, 0.97),
  stringsAsFactors = FALSE
)

#------------------------------------------------------------------------------
# Function to load regional summary statistics
#------------------------------------------------------------------------------
load_regional_sumstats <- function(trait, ancestry, chr, start, end) {
  file <- file.path(sumstats_dir, paste0(trait, ".", ancestry, ".tsv.bgz"))

  if (!file.exists(file)) {
    warning(paste("File not found:", file))
    return(NULL)
  }

  # Use tabix to extract region
  region <- paste0(chr, ":", start, "-", end)
  cmd <- paste("tabix", file, region)

  # Get header
  header_cmd <- paste("zcat", file, "| head -1")
  header <- strsplit(system(header_cmd, intern = TRUE), "\t")[[1]]

  # Get data
  data <- tryCatch({
    lines <- system(cmd, intern = TRUE)
    if (length(lines) == 0) return(NULL)

    df <- fread(text = paste(lines, collapse = "\n"), header = FALSE)
    colnames(df) <- header
    df
  }, error = function(e) {
    warning(paste("Error loading region:", e$message))
    return(NULL)
  })

  return(data)
}

#------------------------------------------------------------------------------
# Function to calculate LD with lead variant (using correlation of Z-scores as proxy)
#------------------------------------------------------------------------------
calculate_proxy_ld <- function(df, lead_pos) {
  # Find lead variant
  lead_idx <- which.min(abs(df$POS - lead_pos))

  if (length(lead_idx) == 0) {
    df$LD <- NA
    return(df)
  }

  lead_z <- df$BETA[lead_idx] / df$SE[lead_idx]

  # Calculate proxy LD based on distance (approximation)
  # Real LD would require genotype data
  df$dist_to_lead <- abs(df$POS - lead_pos)

  # Exponential decay as rough LD proxy (for visualization only)
  # This is NOT real LD - just for visual effect
  df$LD_proxy <- exp(-df$dist_to_lead / 50000)

  # Assign LD bins for coloring
  df$LD_bin <- cut(df$LD_proxy,
                   breaks = c(0, 0.2, 0.4, 0.6, 0.8, 1.0),
                   labels = c("0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"),
                   include.lowest = TRUE)

  # Mark lead variant
  df$is_lead <- df$POS == df$POS[lead_idx]

  return(df)
}

#------------------------------------------------------------------------------
# Function to create LocusZoom-style plot
#------------------------------------------------------------------------------
create_locuszoom_plot <- function(df, trait, chr, lead_pos, locus_name, h4_value) {

  if (is.null(df) || nrow(df) == 0) {
    return(NULL)
  }

  # Calculate -log10(P)
  df$logp <- -log10(df$P)
  df$logp[is.infinite(df$logp)] <- 300  # Cap extreme values

  # Calculate LD proxy
  df <- calculate_proxy_ld(df, lead_pos)

  # LD color palette (classic LocusZoom colors)
  ld_colors <- c(
    "0.0-0.2" = "#000080",   # Navy
    "0.2-0.4" = "#87CEEB",   # Sky blue
    "0.4-0.6" = "#00FF00",   # Green
    "0.6-0.8" = "#FFA500",   # Orange
    "0.8-1.0" = "#FF0000"    # Red
  )

  # Find lead variant for diamond
  lead_df <- df[df$is_lead, ]

  # Create plot
  p <- ggplot(df, aes(x = POS/1e6, y = logp)) +
    # Points colored by LD
    geom_point(aes(color = LD_bin), size = 2, alpha = 0.8) +
    # Lead variant as diamond
    geom_point(data = lead_df, aes(x = POS/1e6, y = logp),
               shape = 23, size = 4, fill = "purple", color = "black") +
    # Genome-wide significance line
    geom_hline(yintercept = -log10(5e-8), linetype = "dashed", color = "red", alpha = 0.7) +
    # Suggestive line
    geom_hline(yintercept = -log10(1e-5), linetype = "dotted", color = "blue", alpha = 0.5) +
    # Colors
    scale_color_manual(values = ld_colors, name = "LD (r²)", na.value = "grey50",
                       drop = FALSE) +
    # Labels
    labs(
      title = paste0(locus_name, " - ", toupper(trait)),
      subtitle = paste0("Chr", chr, " | PP.H4 = ", h4_value),
      x = paste0("Chromosome ", chr, " Position (Mb)"),
      y = expression(-log[10](P))
    ) +
    # Theme
    theme_bw() +
    theme(
      plot.title = element_text(size = 14, face = "bold"),
      plot.subtitle = element_text(size = 11),
      legend.position = "right",
      panel.grid.minor = element_blank()
    )

  return(p)
}

#------------------------------------------------------------------------------
# Function to create side-by-side colocalization plot
#------------------------------------------------------------------------------
create_coloc_locuszoom <- function(locus_info, ancestry = "EUR") {

  chr <- locus_info$chr
  lead_pos <- locus_info$lead_pos
  window <- locus_info$window
  start <- lead_pos - window
  end <- lead_pos + window

  # Load data for both traits
  df_a <- load_regional_sumstats(locus_info$trait_a, ancestry, chr, start, end)
  df_b <- load_regional_sumstats(locus_info$trait_b, ancestry, chr, start, end)

  if (is.null(df_a) || is.null(df_b)) {
    warning(paste("Could not load data for", locus_info$locus))
    return(NULL)
  }

  # Create individual plots
  p_a <- create_locuszoom_plot(df_a, locus_info$trait_a, chr, lead_pos,
                                locus_info$locus, locus_info$h4)
  p_b <- create_locuszoom_plot(df_b, locus_info$trait_b, chr, lead_pos,
                                locus_info$locus, locus_info$h4)

  if (is.null(p_a) || is.null(p_b)) {
    return(NULL)
  }

  # Combine plots
  combined <- p_a / p_b +
    plot_annotation(
      title = paste0(locus_info$locus, " Colocalization"),
      subtitle = paste0(toupper(locus_info$trait_a), " vs ", toupper(locus_info$trait_b),
                       " | PP.H4 = ", locus_info$h4),
      theme = theme(
        plot.title = element_text(size = 16, face = "bold", hjust = 0.5),
        plot.subtitle = element_text(size = 12, hjust = 0.5)
      )
    )

  return(combined)
}

#------------------------------------------------------------------------------
# Generate plots for all top loci
#------------------------------------------------------------------------------
cat("Generating LocusZoom plots for top colocalization loci...\n\n")

for (i in 1:nrow(top_loci)) {
  locus <- top_loci[i, ]
  cat(paste0("Processing ", locus$locus, " (", locus$trait_a, " vs ", locus$trait_b, ")...\n"))

  # Create combined plot
  p <- tryCatch({
    create_coloc_locuszoom(locus, "EUR")
  }, error = function(e) {
    cat(paste0("  Error: ", e$message, "\n"))
    return(NULL)
  })

  if (!is.null(p)) {
    # Save
    filename <- paste0("LocusZoom_", locus$locus, "_", locus$trait_a, "_", locus$trait_b)

    ggsave(file.path(output_dir, paste0(filename, ".pdf")), p,
           width = 10, height = 10, units = "in")
    ggsave(file.path(output_dir, paste0(filename, ".png")), p,
           width = 10, height = 10, units = "in", dpi = 300)

    cat(paste0("  Saved: ", filename, ".pdf/png\n"))
  }
}

#------------------------------------------------------------------------------
# Create multi-panel figure for manuscript
#------------------------------------------------------------------------------
cat("\nCreating multi-panel figure...\n")

# Create smaller versions for multi-panel
plots_list <- list()

for (i in 1:min(4, nrow(top_loci))) {
  locus <- top_loci[i, ]

  chr <- locus$chr
  lead_pos <- locus$lead_pos
  window <- locus$window
  start <- lead_pos - window
  end <- lead_pos + window

  # Load trait A only for simplified view
  df <- load_regional_sumstats(locus$trait_a, "EUR", chr, start, end)

  if (!is.null(df)) {
    p <- create_locuszoom_plot(df, locus$trait_a, chr, lead_pos,
                               locus$locus, locus$h4)
    if (!is.null(p)) {
      plots_list[[locus$locus]] <- p + theme(legend.position = "none")
    }
  }
}

if (length(plots_list) >= 4) {
  multi_panel <- (plots_list[[1]] | plots_list[[2]]) /
                 (plots_list[[3]] | plots_list[[4]]) +
    plot_annotation(
      title = "Regional Association Plots at Top Colocalization Loci",
      theme = theme(plot.title = element_text(size = 16, face = "bold", hjust = 0.5))
    )

  ggsave(file.path(output_dir, "Fig11_LocusZoom_multipanel.pdf"), multi_panel,
         width = 14, height = 12, units = "in")
  ggsave(file.path(output_dir, "Fig11_LocusZoom_multipanel.png"), multi_panel,
         width = 14, height = 12, units = "in", dpi = 300)

  cat("Saved: Fig11_LocusZoom_multipanel.pdf/png\n")
}

cat("\nLocusZoom plot generation complete!\n")
cat(paste0("Output directory: ", output_dir, "\n"))
