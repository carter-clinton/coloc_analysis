#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
  library(scales)
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
  if (!all(c("CHR", "POS") %in% names(dt))) return(NULL)
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

plots_dir <- file.path("results", "plots")
dir.create(plots_dir, recursive = TRUE, showWarnings = FALSE)

regions <- fread("config/regions_tiled.csv")
region_bounds <- regions[, .(
  chr = first(chr),
  start = min(start),
  end = max(end)
), by = .(region_name = parent_region)]

pip_summary <- fread("results/fine_mapping/a_list_pip_summary.tsv")

get_top_snps <- function(region, anc, traits) {
  sub <- pip_summary[base_region == region & ancestry == anc & trait %in% traits]
  if (nrow(sub) == 0) return(list(top = data.table(), shared = character()))
  sub <- sub[order(-top_pip)]
  top <- sub[, .SD[1], by = .(trait)]
  counts <- table(top$top_snp)
  shared <- names(counts[counts > 1])
  top[, shared := top_snp %in% shared]
  list(top = top, shared = shared)
}

make_overlay_plot <- function(region, anc, traits, outfile) {
  bounds <- region_bounds[region_name == region]
  if (nrow(bounds) == 0) {
    message("No bounds for ", region)
    return(NULL)
  }
  chr <- bounds$chr[1]
  start_bp <- max(0, bounds$start[1] - 250000)
  end_bp <- bounds$end[1] + 250000
  sum_list <- lapply(traits, function(tr) read_sumstats_window(tr, anc, chr, start_bp, end_bp))
  sum_list <- sum_list[!sapply(sum_list, is.null)]
  if (length(sum_list) == 0) {
    message("No sumstats for ", region, " ", anc)
    return(NULL)
  }
  df <- rbindlist(sum_list, fill = TRUE)
  df[, trait := factor(trait, levels = traits)]
  snp_info <- get_top_snps(region, anc, traits)
  top <- snp_info$top
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
      title = paste0(region, " (", anc, ")"),
      subtitle = paste0("chr", chr, ":", comma(start_bp), "-", comma(end_bp)),
      x = "Position (bp)",
      y = expression(-log[10](P))
    ) +
    theme_minimal() +
    theme(legend.title = element_blank(), legend.position = "top")
  if (nrow(top) > 0) {
    top <- top[!is.na(top_pos)]
    if (nrow(top) > 0) {
      p <- p +
        geom_point(data = top, aes(x = top_pos, y = max(df$LOGP, na.rm = TRUE) * 1.02),
                   inherit.aes = FALSE, size = 2.5, color = "black") +
        geom_text(data = top, aes(x = top_pos, y = max(df$LOGP, na.rm = TRUE) * 1.05,
                                  label = top_snp),
                  inherit.aes = FALSE, angle = 45, hjust = 0, size = 2.3,
                  color = ifelse(top$shared, "black", "grey30"))
    }
  }
  ggsave(outfile, p, width = 8, height = 4, dpi = 200)
  message("Wrote ", outfile)
}

overlay_specs <- list(
  list(region = "TCF7L2_10q25", anc = "EUR", traits = c("bmi", "t2d")),
  list(region = "BMI_5q13.3", anc = "EUR", traits = c("bmi", "t2d")),
  list(region = "FTO_16q12", anc = "EUR", traits = c("bmi", "t2d")),
  list(region = "KCNJ11_ABCC8_11p15", anc = "EUR", traits = c("bmi", "t2d")),
  list(region = "SH2B3_12q24", anc = "EUR", traits = c("bmi", "stroke")),
  list(region = "RAD50_IL13_5q31.1", anc = "AFR", traits = c("stroke", "t2d")),
  list(region = "HHEX_10q23", anc = "AFR", traits = c("stroke", "t2d"))
)

for (spec in overlay_specs) {
  outfile <- file.path(plots_dir, paste0("overlay_", spec$region, "_", spec$anc, ".png"))
  make_overlay_plot(spec$region, spec$anc, spec$traits, outfile)
}

extract_variants <- function(region, pip_threshold = 0.05) {
  files <- list.files("results/fine_mapping/susie", pattern = paste0(region, ".*\\.json$"), full.names = TRUE)
  rows <- list()
  for (path in files) {
    j <- tryCatch(jsonlite::fromJSON(path), error = function(e) NULL)
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
    cs_rows[, base_region := region]
    rows[[length(rows) + 1]] <- cs_rows
  }
  if (length(rows) == 0) return(NULL)
  rbindlist(rows, fill = TRUE)
}

make_violin_plot <- function(region, traits, ancestries) {
  dt <- extract_variants(region, pip_threshold = 0.05)
  if (is.null(dt)) return(NULL)
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
    labs(x = "Ancestry", y = "Beta", title = paste0(region, " effect distribution (pip ≥ 0.05)")) +
    theme_minimal() +
    theme(legend.position = "none")
  p
}

make_forest_plot <- function(region, traits, ancestries) {
  df <- pip_summary[base_region == region & trait %in% traits & ancestry %in% ancestries]
  if (nrow(df) == 0) return(NULL)
  df <- df[order(-top_pip)]
  df <- df[, .SD[1], by = .(trait, ancestry)]
  df[, ci_low := top_beta - 1.96 * top_se]
  df[, ci_high := top_beta + 1.96 * top_se]
  p <- ggplot(df, aes(x = trait, y = top_beta, color = ancestry)) +
    geom_point(position = position_dodge(width = 0.4), size = 2) +
    geom_errorbar(aes(ymin = ci_low, ymax = ci_high), width = 0.2,
                  position = position_dodge(width = 0.4)) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
    labs(x = "Trait", y = "Beta (top PIP)") +
    theme_minimal()
  p
}

make_combo_panel <- function(region, traits, ancestries, outfile) {
  vplot <- make_violin_plot(region, traits, ancestries)
  fplot <- make_forest_plot(region, traits, ancestries)
  if (is.null(vplot) && is.null(fplot)) return(NULL)
  png(outfile, width = 1600, height = 700, res = 200)
  grid.newpage()
  pushViewport(viewport(layout = grid.layout(1, 2)))
  if (!is.null(vplot)) print(vplot, vp = viewport(layout.pos.row = 1, layout.pos.col = 1))
  if (!is.null(fplot)) print(fplot, vp = viewport(layout.pos.row = 1, layout.pos.col = 2))
  dev.off()
  message("Wrote ", outfile)
}

combo_specs <- list(
  list(region = "TCF7L2_10q25", traits = c("bmi", "t2d"), ancestries = c("EUR", "AFR", "TRANS")),
  list(region = "RAD50_IL13_5q31.1", traits = c("stroke", "t2d"), ancestries = c("AFR", "EUR")),
  list(region = "SH2B3_12q24", traits = c("bmi", "stroke"), ancestries = c("EUR", "AFR"))
)

for (spec in combo_specs) {
  outfile <- file.path(plots_dir, paste0("panel_violin_forest_", spec$region, ".png"))
  make_combo_panel(spec$region, spec$traits, spec$ancestries, outfile)
}
