#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
  library(scales)
  library(jsonlite)
  library(grid)
})

sumstats_path <- function(trait, ancestry) {
  fixed <- file.path("data_processed", "sumstats_harmonized_fixed",
                     sprintf("%s.%s.tsv.bgz", trait, ancestry))
  if (file.exists(fixed)) {
    return(fixed)
  }
  file.path("data_processed", "sumstats_harmonized",
            sprintf("%s.%s.tsv.bgz", trait, ancestry))
}

read_sumstats_window <- function(trait, ancestry, chr, start_bp, end_bp) {
  path <- sumstats_path(trait, ancestry)
  if (!file.exists(path)) return(NULL)
  cmd <- sprintf("gunzip -c %s", shQuote(path))
  dt <- tryCatch(fread(cmd), error = function(e) NULL)
  if (is.null(dt)) return(NULL)
  if (!("CHR" %in% names(dt)) || !("POS" %in% names(dt))) return(NULL)
  if (!("P" %in% names(dt)) && all(c("BETA", "SE") %in% names(dt))) {
    beta_vals <- as.numeric(dt[["BETA"]])
    se_vals <- as.numeric(dt[["SE"]])
    z <- abs(beta_vals / se_vals)
    dt[, P := 2 * pnorm(-z)]
  }
  if (!("P" %in% names(dt))) return(NULL)
  dt[, CHR := gsub("^chr", "", CHR, ignore.case = TRUE)]
  dt[, CHR := as.character(CHR)]
  dt[, POS := as.numeric(POS)]
  dt[, P := as.numeric(P)]
  dt <- dt[CHR == as.character(chr) & POS >= start_bp & POS <= end_bp]
  if (nrow(dt) == 0) return(NULL)
  dt[, LOGP := -log10(pmax(P, 1e-300))]
  dt[, trait := trait]
  dt[, ancestry := ancestry]
  dt
}

extract_variants <- function(base_region, pip_threshold = 0.05) {
  files <- list.files("results/fine_mapping/susie", pattern = paste0(base_region, ".*\\.json$"), full.names = TRUE)
  rows <- list()
  for (path in files) {
    j <- tryCatch(fromJSON(path), error = function(e) NULL)
    if (is.null(j)) next
    if (!identical(j$status, "success")) next
    cs_list <- j$credible_sets
    if (is.null(cs_list) || length(cs_list) == 0) next
    cs_rows <- rbindlist(lapply(names(cs_list), function(cs_name) {
      dt <- as.data.table(cs_list[[cs_name]])
      dt[, cs := cs_name]
      dt
    }), fill = TRUE)
    if (!("pip" %in% names(cs_rows)) && "PIP" %in% names(cs_rows)) {
      setnames(cs_rows, "PIP", "pip")
    }
    if (!("BETA" %in% names(cs_rows)) && "beta" %in% names(cs_rows)) {
      setnames(cs_rows, "beta", "BETA")
    }
    if (!("SE" %in% names(cs_rows)) && "se" %in% names(cs_rows)) {
      setnames(cs_rows, "se", "SE")
    }
    cs_rows[, pip := as.numeric(pip)]
    cs_rows <- cs_rows[!is.na(pip) & pip >= pip_threshold]
    if (nrow(cs_rows) == 0) next
    cs_rows[, trait := j$trait]
    cs_rows[, ancestry := j$ancestry]
    cs_rows[, base_region := base_region]
    rows[[length(rows) + 1]] <- cs_rows
  }
  if (length(rows) == 0) return(NULL)
  rbindlist(rows, fill = TRUE)
}

plots_dir <- file.path("results", "plots")
dir.create(plots_dir, recursive = TRUE, showWarnings = FALSE)

regions <- fread("config/regions_tiled.csv")
region_bounds <- regions[, .(
  chr = first(chr),
  start = min(start),
  end = max(end)
), by = .(region_name = parent_region)]

pip_summary <- fread("results/fine_mapping/a_list_pip_summary.tsv")

make_local_plot <- function(base_region, ancestry, traits) {
  bounds <- region_bounds[region_name == base_region]
  if (nrow(bounds) == 0) return(NULL)
  chr <- bounds$chr[1]
  start_bp <- max(0, bounds$start[1] - 250000)
  end_bp <- bounds$end[1] + 250000
  sum_list <- lapply(traits, function(tr) read_sumstats_window(tr, ancestry, chr, start_bp, end_bp))
  sum_list <- sum_list[!sapply(sum_list, is.null)]
  if (length(sum_list) == 0) return(NULL)
  df <- rbindlist(sum_list, fill = TRUE)
  df[, trait := factor(trait, levels = traits)]
  pip_rows <- pip_summary[
    base_region == base_region &
      ancestry == ancestry &
      trait %in% traits
  ]
  top_snps <- pip_rows[order(-top_pip)][1:min(6, nrow(pip_rows))]
  p <- ggplot(df, aes(x = POS, y = LOGP, color = trait)) +
    geom_point(alpha = 0.6, size = 0.8) +
    scale_color_manual(values = c(
      bmi = "#1f77b4",
      t2d = "#d62728",
      stroke = "#2ca02c",
      asthma = "#9467bd",
      hypertension = "#8c564b"
    ), drop = FALSE) +
    labs(
      title = paste0(base_region, " (", ancestry, ")"),
      subtitle = paste0("chr", chr, ":", comma(start_bp), "-", comma(end_bp)),
      x = "Position (bp)",
      y = expression(-log[10](P))
    ) +
    theme_minimal() +
    theme(legend.title = element_blank(), legend.position = "top")
  if (nrow(top_snps) > 0) {
    p <- p +
      geom_point(data = top_snps, aes(x = top_pos, y = max(df$LOGP, na.rm = TRUE) * 1.02),
                 inherit.aes = FALSE, size = 2.5, color = "black") +
      geom_text(data = top_snps, aes(x = top_pos, y = max(df$LOGP, na.rm = TRUE) * 1.05,
                                     label = top_snp),
                inherit.aes = FALSE, angle = 45, hjust = 0, size = 2.3)
  }
  p
}

regional_specs <- list(
  list(region = "FTO_16q12", ancestry = "EUR", traits = c("bmi", "t2d")),
  list(region = "BMI_5q13.3", ancestry = "EUR", traits = c("bmi", "t2d")),
  list(region = "TCF7L2_10q25", ancestry = "EUR", traits = c("bmi", "t2d")),
  list(region = "SH2B3_12q24", ancestry = "EUR", traits = c("bmi", "stroke")),
  list(region = "RAD50_IL13_5q31.1", ancestry = "AFR", traits = c("stroke", "t2d")),
  list(region = "HHEX_10q23", ancestry = "AFR", traits = c("stroke", "t2d"))
)

regional_plots <- lapply(regional_specs, function(spec) {
  make_local_plot(spec$region, spec$ancestry, spec$traits)
})

png(file.path(plots_dir, "panel_regional_pip.png"), width = 2000, height = 1200, res = 200)
grid.newpage()
pushViewport(viewport(layout = grid.layout(2, 3)))
for (i in seq_along(regional_plots)) {
  p <- regional_plots[[i]]
  if (is.null(p)) next
  row <- ((i - 1) %/% 3) + 1
  col <- ((i - 1) %% 3) + 1
  print(p, vp = viewport(layout.pos.row = row, layout.pos.col = col))
}
dev.off()

make_violin <- function(base_region, traits, ancestries, outfile) {
  dt <- extract_variants(base_region, pip_threshold = 0.05)
  if (is.null(dt)) {
    message("No variant data for ", base_region)
    return(NULL)
  }
  dt <- dt[trait %in% traits & ancestry %in% ancestries]
  dt[, BETA := as.numeric(BETA)]
  dt <- dt[!is.na(BETA)]
  if (nrow(dt) == 0) return(NULL)
  dt[, trait := factor(trait, levels = traits)]
  p <- ggplot(dt, aes(x = ancestry, y = BETA, fill = ancestry)) +
    geom_violin(aes(weight = pip), trim = TRUE, alpha = 0.5) +
    geom_jitter(width = 0.1, size = 1, alpha = 0.5) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
    facet_wrap(~trait, scales = "free_y") +
    labs(
      title = paste0(base_region, " effect distribution (pip ≥ 0.05)"),
      x = "Ancestry",
      y = "Beta"
    ) +
    theme_minimal() +
    theme(legend.position = "none")
  ggsave(outfile, p, width = 6, height = 4, dpi = 200)
  message("Wrote ", outfile)
}

make_violin("TCF7L2_10q25", c("bmi", "t2d"), c("EUR", "AFR", "TRANS"),
            file.path(plots_dir, "violin_TCF7L2_bmi_t2d.png"))
make_violin("RAD50_IL13_5q31.1", c("stroke", "t2d"), c("AFR", "EUR"),
            file.path(plots_dir, "violin_RAD50_stroke_t2d.png"))

make_effect_plot <- function(base_region, traits, ancestries, title) {
  df <- fread("results/fine_mapping/a_list_pip_summary.tsv")
  sub <- df[base_region == base_region & trait %in% traits & ancestry %in% ancestries]
  sub <- sub[order(-top_pip)]
  sub <- sub[, .SD[1], by = .(trait, ancestry)]
  if (nrow(sub) == 0) return(NULL)
  sub[, ci_low := top_beta - 1.96 * top_se]
  sub[, ci_high := top_beta + 1.96 * top_se]
  p <- ggplot(sub, aes(x = trait, y = top_beta, color = ancestry)) +
    geom_point(position = position_dodge(width = 0.4), size = 2) +
    geom_errorbar(aes(ymin = ci_low, ymax = ci_high), width = 0.2,
                  position = position_dodge(width = 0.4)) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
    labs(title = title, x = "Trait", y = "Beta (top PIP)") +
    theme_minimal()
  p
}

p1 <- make_effect_plot("TCF7L2_10q25", c("bmi", "t2d"), c("EUR", "AFR", "TRANS"),
                       "TCF7L2_10q25 effect sizes")
p2 <- make_effect_plot("RAD50_IL13_5q31.1", c("stroke", "t2d"), c("AFR", "EUR"),
                       "RAD50_IL13_5q31.1 effect sizes")

png(file.path(plots_dir, "panel_effects.png"), width = 1200, height = 600, res = 200)
grid.newpage()
pushViewport(viewport(layout = grid.layout(1, 2)))
if (!is.null(p1)) print(p1, vp = viewport(layout.pos.row = 1, layout.pos.col = 1))
if (!is.null(p2)) print(p2, vp = viewport(layout.pos.row = 1, layout.pos.col = 2))
dev.off()
