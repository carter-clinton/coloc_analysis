#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
  library(scales)
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
  if (!file.exists(path)) {
    message("Missing sumstats for ", trait, ".", ancestry)
    return(NULL)
  }
  cmd <- sprintf("gunzip -c %s", shQuote(path))
  dt <- tryCatch(fread(cmd), error = function(e) NULL)
  if (is.null(dt)) return(NULL)
  if (!("CHR" %in% names(dt)) || !("POS" %in% names(dt))) {
    message("Missing columns in ", path)
    return(NULL)
  }
  if (!("P" %in% names(dt)) && all(c("BETA", "SE") %in% names(dt))) {
    beta_vals <- as.numeric(dt[["BETA"]])
    se_vals <- as.numeric(dt[["SE"]])
    z <- abs(beta_vals / se_vals)
    dt[, P := 2 * pnorm(-z)]
  }
  if (!("P" %in% names(dt))) {
    message("Missing P in ", path)
    return(NULL)
  }
  dt[, CHR := gsub("^chr", "", CHR, ignore.case = TRUE)]
  dt[, CHR := as.character(CHR)]
  chr_target <- as.character(chr)
  dt <- dt[CHR == chr_target]
  if (nrow(dt) == 0) return(NULL)
  dt[, POS := as.numeric(POS)]
  dt <- dt[POS >= start_bp & POS <= end_bp]
  if (!("BETA" %in% names(dt))) dt[, BETA := NA_real_]
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

local_specs <- data.table(
  region = c(
    "FTO_16q12",
    "BMI_5q13.3",
    "TCF7L2_10q25",
    "SH2B3_12q24",
    "RAD50_IL13_5q31.1",
    "HHEX_10q23"
  ),
  anc = c("EUR", "EUR", "EUR", "EUR", "AFR", "AFR"),
  traits = I(list(
    c("bmi", "t2d"),
    c("bmi", "t2d"),
    c("bmi", "t2d"),
    c("bmi", "stroke"),
    c("stroke", "t2d"),
    c("stroke", "t2d")
  )),
  outfile = c(
    "pip_FTO_EUR_bmi_t2d.png",
    "pip_BMI5q13_EUR_bmi_t2d.png",
    "pip_TCF7L2_EUR_bmi_t2d.png",
    "pip_SH2B3_EUR_bmi_stroke.png",
    "pip_RAD50_IL13_AFR_stroke_t2d.png",
    "pip_HHEX_AFR_stroke_t2d.png"
  )
)

for (i in seq_len(nrow(local_specs))) {
  region <- local_specs$region[i]
  anc <- local_specs$anc[i]
  traits <- local_specs$traits[[i]]
  outfile <- local_specs$outfile[i]
    bounds <- region_bounds[region_name == region]
    if (nrow(bounds) == 0) {
      message("No bounds for ", region)
      next
    }
    chr <- bounds$chr[1]
    start_bp <- max(0, bounds$start[1] - 250000)
    end_bp <- bounds$end[1] + 250000
    sum_list <- lapply(traits, function(tr) {
      read_sumstats_window(tr, anc, chr, start_bp, end_bp)
    })
    sum_list <- sum_list[!sapply(sum_list, is.null)]
    if (length(sum_list) == 0) {
      message("No sumstats for ", region, " ", anc)
      next
    }
    df <- rbindlist(sum_list, fill = TRUE)
    df[, trait := factor(trait, levels = traits)]
    pip_rows <- pip_summary[
      base_region == region &
        ancestry == anc &
        trait %in% traits
    ]
    p <- ggplot(df, aes(x = POS, y = LOGP, color = trait)) +
      geom_point(alpha = 0.6, size = 0.8) +
      scale_color_manual(values = c(
        bmi = "#1f77b4",
        t2d = "#d62728",
        stroke = "#2ca02c",
        asthma = "#9467bd",
        hypertension = "#8c564b"
      ),
      drop = FALSE) +
      labs(
        title = paste0(region, " (", anc, ")"),
        subtitle = paste0("chr", chr, ":", comma(start_bp), "-", comma(end_bp)),
        x = "Position (bp)",
        y = expression(-log[10](P))
      ) +
      theme_minimal() +
      theme(
        legend.title = element_blank(),
        legend.position = "top"
      )
    if (nrow(pip_rows) > 0) {
      p <- p +
        geom_point(
          data = pip_rows,
          aes(
            x = top_pos,
            y = max(df$LOGP, na.rm = TRUE) * 1.02,
            shape = "PIP"
          ),
          inherit.aes = FALSE,
          size = 3,
          color = "black"
        ) +
        geom_text(
          data = pip_rows,
          aes(
            x = top_pos,
            y = max(df$LOGP, na.rm = TRUE) * 1.05,
            label = top_snp
          ),
          inherit.aes = FALSE,
          angle = 45,
          hjust = 0,
          size = 2.5
        ) +
        scale_shape_manual(values = c(PIP = 4), guide = FALSE)
    }
    outfile_path <- file.path(plots_dir, outfile)
    ggsave(outfile_path, p, width = 8, height = 4, dpi = 200)
    message("Wrote ", outfile_path)
}

region_dt <- region_bounds[, .(
  chr = as.integer(chr),
  start = as.numeric(start),
  end = as.numeric(end),
  base_region = region_name
)]
setkey(region_dt, chr, start, end)

trait_ancestry <- data.table(
  trait = c(
    "bmi",
    "t2d",
    "t2d",
    "t2d",
    "asthma",
    "asthma",
    "stroke",
    "stroke",
    "hypertension"
  ),
  ancestry = c(
    "EUR",
    "EUR",
    "AFR",
    "TRANS",
    "EUR",
    "AFR",
    "EUR",
    "AFR",
    "EUR"
  )
)

for (i in seq_len(nrow(trait_ancestry))) {
  tr <- trait_ancestry$trait[i]
  anc <- trait_ancestry$ancestry[i]
  path <- sumstats_path(tr, anc)
  if (!file.exists(path)) {
    message("Skipping global Manhattan for ", tr, ".", anc)
    next
  }
  cmd <- sprintf("gunzip -c %s", shQuote(path))
  dt <- tryCatch(fread(cmd, select = c("CHR", "POS", "P", "BETA", "SE")), error = function(e) NULL)
  if (is.null(dt) || nrow(dt) == 0) next
  dt[, CHR := gsub("^chr", "", CHR, ignore.case = TRUE)]
  suppressWarnings(dt[, CHR := as.integer(CHR)])
  dt <- dt[CHR %in% 1:22]
  dt[, POS := as.numeric(POS)]
  if (!("P" %in% names(dt)) && all(c("BETA", "SE") %in% names(dt))) {
    beta_vals <- as.numeric(dt[["BETA"]])
    se_vals <- as.numeric(dt[["SE"]])
    z <- abs(beta_vals / se_vals)
    dt[, P := 2 * pnorm(-z)]
  }
  dt[, P := as.numeric(P)]
  dt <- dt[!is.na(POS) & !is.na(P)]
  dt[, LOGP := -log10(pmax(P, 1e-300))]
  setorder(dt, CHR, POS)
  chr_info <- dt[, .(chr_len = max(POS, na.rm = TRUE)), by = CHR]
  chr_info[, cum_start := cumsum(shift(chr_len, fill = 0))]
  dt <- merge(dt, chr_info[, .(CHR, offset = cum_start)], by = "CHR", all.x = TRUE)
  dt[, pos_cum := POS + offset]
  dt[, idx := .I]
  dt_dt <- dt[, .(idx, CHR, start = POS, end = POS)]
  setkey(dt_dt, CHR, start, end)
  overlap <- foverlaps(dt_dt, region_dt,
                       by.x = c("CHR", "start", "end"),
                       nomatch = 0L)
  dt[, base_region := NA_character_]
  if (nrow(overlap) > 0) {
    dt[overlap$idx, base_region := overlap$base_region]
  }
  dt[, chr_label := factor(CHR)]
  base_colors <- rep(c("#bbbbbb", "#888888"), length.out = 22)
  names(base_colors) <- as.character(1:22)
  p <- ggplot(dt, aes(x = pos_cum, y = LOGP)) +
    geom_point(aes(color = chr_label), alpha = 0.6, size = 0.4) +
    scale_color_manual(values = base_colors, guide = "none") +
    geom_point(
      data = dt[!is.na(base_region)],
      aes(x = pos_cum, y = LOGP),
      color = "#d62728",
      size = 0.8,
      alpha = 0.7
    ) +
    labs(
      title = paste0("Global Manhattan: ", tr, " (", anc, ")"),
      x = "Chromosome",
      y = expression(-log[10](P))
    ) +
    theme_minimal()
  chr_centers <- chr_info[, .(CHR, center = cum_start + chr_len / 2)]
  p <- p + scale_x_continuous(
    breaks = chr_centers$center,
    labels = chr_centers$CHR
  )
  outfile <- file.path(
    plots_dir,
    sprintf("manhattan_%s_%s.png", tr, anc)
  )
  ggsave(outfile, p, width = 10, height = 4, dpi = 200)
  message("Wrote ", outfile)
}

counts <- fread("results/multitrait/coloc_shared_counts.tsv")
counts$trait_a <- sapply(strsplit(counts$trait_pair, "__"), `[`, 1)
counts$trait_b <- sapply(strsplit(counts$trait_pair, "__"), `[`, 2)
counts$trait_label <- paste(counts$trait_pair, counts$ancestry, sep = "_")

bar_plot <- ggplot(counts, aes(x = trait_pair, y = n_loci, fill = ancestry)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.7)) +
  labs(
    title = "Shared causal loci (PP.H4 ≥ 0.8)",
    x = "Trait pair",
    y = "# loci"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(file.path(plots_dir, "coloc_shared_bar.png"), bar_plot,
       width = 6, height = 4, dpi = 200)

dot_plot <- ggplot(counts, aes(x = trait_pair, y = n_loci, color = ancestry)) +
  geom_point(position = position_dodge(width = 0.6), size = 3) +
  labs(
    title = "Shared causal loci (dot plot)",
    x = "Trait pair",
    y = "# loci"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(file.path(plots_dir, "coloc_shared_dot.png"), dot_plot,
       width = 6, height = 4, dpi = 200)
