#!/usr/bin/env Rscript
# D-25 trait facts measured inside the admissible regions: N median, |BETA| / SE medians, and the
# per-region coloc:::sdY.est(SE^2, MAF, N) median (for the record). One TSV row per trait x ancestry.
#   Rscript measure_trait_facts.R --tabix T --regions regions_r4.csv --region-safe a,b,... \
#       --inputs trait:anc:path,... --out facts.tsv
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
})

opt <- parse_args(OptionParser(option_list = list(
  make_option("--tabix"), make_option("--regions"), make_option("--region-safe"),
  make_option("--inputs"), make_option("--out"))))
reg <- fread(opt$regions)
reg[, region_safe := gsub("[./]", "_", region_id)]
reg <- reg[region_safe %in% strsplit(opt$`region-safe`, ",")[[1]]]

rows <- list()
for (spec in strsplit(opt$inputs, ",")[[1]]) {
  p <- strsplit(spec, ":")[[1]]
  trait <- p[1]; anc <- p[2]; path <- p[3]
  hdr <- names(fread(cmd = sprintf("gunzip -c %s | head -1", shQuote(path))))
  per <- list()
  for (i in seq_len(nrow(reg))) {
    q <- sprintf("%s:%d-%d", reg$chr[i], reg$start[i], reg$end[i])
    d <- fread(cmd = paste(shQuote(opt$tabix), shQuote(path), q), header = FALSE, col.names = hdr)
    if (!nrow(d)) next
    d[, region_safe := reg$region_safe[i]]
    per[[i]] <- d
  }
  d <- rbindlist(per)
  sdy <- NA_real_; n_sdy <- 0L
  if ("EAF" %in% names(d)) {
    est <- sapply(split(d, d$region_safe), function(x) {
      x <- x[is.finite(SE) & SE > 0 & is.finite(EAF) & EAF > 0 & EAF < 1 & is.finite(N)]
      if (nrow(x) < 50) return(NA_real_)
      suppressWarnings(tryCatch(coloc:::sdY.est(x$SE^2, pmin(x$EAF, 1 - x$EAF), x$N), error = function(e) NA_real_))
    })
    n_sdy <- sum(is.finite(est)); sdy <- median(est, na.rm = TRUE)
  }
  rows[[spec]] <- data.table(
    trait = trait, ancestry = anc, n_rows = nrow(d), n_regions = uniqueN(d$region_safe),
    N_median = median(d$N, na.rm = TRUE), N_min = min(d$N, na.rm = TRUE), N_max = max(d$N, na.rm = TRUE),
    absbeta_median = signif(median(abs(d$BETA), na.rm = TRUE), 4), se_median = signif(median(d$SE, na.rm = TRUE), 4),
    has_eaf = "EAF" %in% names(d), sdY_est_median = signif(sdy, 4), sdY_est_n_regions = n_sdy)
}
fwrite(rbindlist(rows), opt$out, sep = "\t")
