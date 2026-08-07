# E-2 exposure measurement on the REAL corpus. READ-ONLY. Uses the SHIPPED
# ld_allele_join_indices() -- never a reimplementation (260805-w7u body-walk rule).
setwd("/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis")
suppressWarnings(suppressMessages(library(data.table)))
source("src/snakemake/scripts/ld_allele_join.R")
stopifnot(is.function(ld_allele_join_indices))

vdir <- "data/processed/region_analysis/ld_reference/variants"
rows <- list()
for (anc in c("EUR","AFR","TRANS")) {
  pdir <- file.path("data/processed/region_analysis/ld_reference", anc)
  for (f in list.files(vdir, pattern="\\.tsv$", full.names=TRUE)) {
    id <- sub("\\.tsv$","",basename(f))
    pf <- file.path(pdir, paste0(id, ".rds"))
    if (!file.exists(pf)) next
    cat_dt <- tryCatch(as.data.frame(fread(f)), error=function(e) NULL)
    if (is.null(cat_dt) || !nrow(cat_dt)) next
    o <- tryCatch(readRDS(pf), error=function(e) NULL)
    pv <- if (is.list(o) && !is.matrix(o)) o$variants else NULL
    if (is.null(pv) || !is.data.frame(pv)) { rm(o); gc(FALSE); next }
    j <- tryCatch(ld_allele_join_indices(cat_dt, pv), error=function(e) NULL)
    rm(o); gc(FALSE)
    if (is.null(j)) next
    cn <- j$counts
    rows[[length(rows)+1]] <- data.frame(
      ancestry=anc, region=id,
      exact=cn$exact, flipped=cn$flipped,
      dropped_ambiguous=cn$dropped_ambiguous, dropped_palindromic=cn$dropped_palindromic,
      dropped_mismatch=cn$dropped_mismatch, dropped_unusable=cn$dropped_unusable,
      reject=ifelse(is.null(cn$reject), NA_character_, cn$reject),
      n_catalog=nrow(cat_dt), n_panel=nrow(pv), stringsAsFactors=FALSE)
  }
}
d <- do.call(rbind, rows)
write.table(d, ".planning/phases/m3-aou-afr-ld-panel-build/e2_exposure_real_corpus.tsv", sep="\t", quote=FALSE, row.names=FALSE)
cat("\n================ E-2 EXPOSURE ON THE REAL CORPUS ================\n")
cat(sprintf("regions measured: %d across %d ancestries\n", nrow(d), length(unique(d$ancestry))))
for (anc in unique(d$ancestry)) {
  s <- d[d$ancestry==anc,]
  e <- sum(s$exact); fl <- sum(s$flipped); den <- e+fl
  cat(sprintf("\n%-6s regions=%3d  exact=%7d  flipped=%6d  ratio=%s\n", anc, nrow(s), e, fl,
      ifelse(den>0, sprintf("%.4f%% (%d/%d)", 100*fl/den, fl, den), "n/a (denominator 0)")))
  cat(sprintf("       dropped: ambiguous=%d palindromic=%d mismatch=%d unusable=%d ; rejects=%d\n",
      sum(s$dropped_ambiguous), sum(s$dropped_palindromic), sum(s$dropped_mismatch),
      sum(s$dropped_unusable), sum(!is.na(s$reject))))
  nz <- s[s$flipped>0,]
  cat(sprintf("       regions with ANY flip: %d of %d\n", nrow(nz), nrow(s)))
}
cat("\n=================================================================\n")
