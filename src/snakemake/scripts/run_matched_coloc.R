#!/usr/bin/env Rscript
# =============================================================================
# Phase 4 Plan 04-02 Task 3 — per-bootstrap coloc.susie re-estimation
#
# Pairs the bootstrap EUR-matched .fit.rds with the FIXED AFR discovery
# .fit.rds (D-01c) and runs coloc::coloc.susie. Reuses Phase 1
# run_coloc_susie.R logic verbatim — same coloc.susie call, same
# Pattern 6 Option A compat layer, same empty-CS guard.
#
# Output:
#   - .rds: full coloc result object
#   - .tsv: per-signal summary with columns:
#       signal_id, pph4, pph3, pph2, pph1, pph0,
#       cs_afr_size, cs_eur_size, lead_variant_afr, lead_variant_eur,
#       lead_sign_agree
#
# CLI:
#   Rscript run_matched_coloc.R \
#     --afr-fit <AFR discovery .fit.rds> \
#     --eur-matched-fit <EUR bootstrap .fit.rds> \
#     --output-rds <coloc result .rds> \
#     --output-tsv <coloc summary .tsv>
# =============================================================================

suppressPackageStartupMessages({
  library(optparse)
  library(coloc)
  library(susieR)
  library(data.table)
})

`%||%` <- function(x, y) if (!is.null(x)) x else y

option_list <- list(
  make_option("--afr-fit", dest = "afr_fit", type = "character",
              help = "Path to AFR discovery .fit.rds (Phase 1, held fixed per D-01c)"),
  make_option("--eur-matched-fit", dest = "eur_matched_fit", type = "character",
              help = "Path to EUR-matched bootstrap .fit.rds"),
  make_option("--output-rds", dest = "output_rds", type = "character",
              help = "Output path for full coloc result .rds"),
  make_option("--output-tsv", dest = "output_tsv", type = "character",
              help = "Output path for per-signal coloc summary .tsv")
)

opt <- parse_args(OptionParser(option_list = option_list))

if (is.null(opt$afr_fit) || is.null(opt$eur_matched_fit) ||
    is.null(opt$output_rds) || is.null(opt$output_tsv)) {
  stop("All of --afr-fit, --eur-matched-fit, --output-rds, --output-tsv are required",
       call. = FALSE)
}

# ---------------------------------------------------------------------------
# Load fits — tryCatch wrapping per T-09-16 uniform failure surface
# ---------------------------------------------------------------------------
result <- tryCatch({
  fit_afr <- readRDS(opt$afr_fit)
  fit_eur <- readRDS(opt$eur_matched_fit)

  # Check for SuSiE failure sentinel from bootstrap driver
  if (inherits(fit_eur, "susie_failure") ||
      isTRUE(fit_eur$status == "susie_failure")) {
    stop("EUR-matched fit is a susie_failure sentinel", call. = FALSE)
  }

  # A6 safety: ensure coloc.susie S3 dispatch finds class("susie")
  if (!inherits(fit_afr, "susie")) class(fit_afr) <- c("susie", class(fit_afr))
  if (!inherits(fit_eur, "susie")) class(fit_eur) <- c("susie", class(fit_eur))

  # ---------------------------------------------------------------------------
  # Empty credible-set guard (Phase 1 Pitfall 6)
  # ---------------------------------------------------------------------------
  cs_afr <- fit_afr$sets$cs %||% list()
  cs_eur <- fit_eur$sets$cs %||% list()

  if (length(cs_afr) == 0 || length(cs_eur) == 0) {
    list(
      status = "no_signal",
      n_cs_afr = length(cs_afr),
      n_cs_eur = length(cs_eur),
      summary = NULL
    )
  } else {
    # Main coloc.susie call — reuses Phase 1 logic verbatim
    # AFR as dataset 1, EUR-matched as dataset 2 (D-01c framing)
    res <- coloc::coloc.susie(fit_afr, fit_eur)
    list(
      status = "success",
      n_cs_afr = length(cs_afr),
      n_cs_eur = length(cs_eur),
      summary = as.data.table(res$summary),
      coloc_result = res,
      fit_afr = fit_afr,
      fit_eur = fit_eur
    )
  }
}, error = function(e) {
  list(
    status = "error",
    error_message = conditionMessage(e),
    n_cs_afr = NA_integer_,
    n_cs_eur = NA_integer_,
    summary = NULL
  )
})

# ---------------------------------------------------------------------------
# Write .rds output
# ---------------------------------------------------------------------------
dir.create(dirname(opt$output_rds), recursive = TRUE, showWarnings = FALSE)
saveRDS(result, opt$output_rds)

# ---------------------------------------------------------------------------
# Write .tsv summary
# ---------------------------------------------------------------------------
dir.create(dirname(opt$output_tsv), recursive = TRUE, showWarnings = FALSE)

if (result$status == "success" && !is.null(result$summary) && nrow(result$summary) > 0) {
  dt <- result$summary
  pp_cols <- c("PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf")

  # Extract per-signal row summaries
  out_rows <- lapply(seq_len(nrow(dt)), function(i) {
    row <- dt[i]

    # CS sizes from the fit objects
    idx1 <- row$idx1 %||% NA_integer_
    idx2 <- row$idx2 %||% NA_integer_

    cs_afr_size <- if (!is.na(idx1) && idx1 <= length(result$n_cs_afr)) {
      # Get CS size from AFR fit (stored on result list for scope safety)
      cs_afr_list <- result$fit_afr$sets$cs %||% list()
      if (idx1 <= length(cs_afr_list)) length(cs_afr_list[[idx1]]) else NA_integer_
    } else NA_integer_

    cs_eur_size <- if (!is.na(idx2) && idx2 <= length(result$n_cs_eur)) {
      cs_eur_list <- result$fit_eur$sets$cs %||% list()
      if (idx2 <= length(cs_eur_list)) length(cs_eur_list[[idx2]]) else NA_integer_
    } else NA_integer_

    # Lead variants (hit1 = AFR CS lead, hit2 = EUR CS lead)
    lead_afr <- row$hit1 %||% NA_character_
    lead_eur <- row$hit2 %||% NA_character_

    # D-02c hook: lead-variant direction-of-effect sign agreement
    lead_sign_agree <- tryCatch({
      if (!is.na(lead_afr) && !is.na(lead_eur) &&
          !is.null(result$fit_afr$mu) && !is.null(result$fit_eur$mu)) {
        # Compare sign of PIP-weighted effect at lead variants
        # This is a sanity check — should be ~100% agreement
        afr_pip <- result$fit_afr$pip
        eur_pip <- result$fit_eur$pip

        if (!is.null(names(afr_pip)) && !is.null(names(eur_pip))) {
          afr_idx <- match(lead_afr, names(afr_pip))
          eur_idx <- match(lead_eur, names(eur_pip))
          if (!is.na(afr_idx) && !is.na(eur_idx) &&
              !is.null(result$fit_afr$mu) && !is.null(result$fit_eur$mu)) {
            # Use alpha-weighted mu for effect direction
            afr_effect <- sum(result$fit_afr$alpha[, afr_idx] * result$fit_afr$mu[, afr_idx])
            eur_effect <- sum(result$fit_eur$alpha[, eur_idx] * result$fit_eur$mu[, eur_idx])
            as.integer(sign(afr_effect) == sign(eur_effect))
          } else NA_integer_
        } else NA_integer_
      } else NA_integer_
    }, error = function(e) NA_integer_)

    signal_id <- paste0("L", idx1, "_L", idx2)

    data.table(
      signal_id = signal_id,
      pph4 = row$PP.H4.abf %||% NA_real_,
      pph3 = row$PP.H3.abf %||% NA_real_,
      pph2 = row$PP.H2.abf %||% NA_real_,
      pph1 = row$PP.H1.abf %||% NA_real_,
      pph0 = row$PP.H0.abf %||% NA_real_,
      cs_afr_size = cs_afr_size,
      cs_eur_size = cs_eur_size,
      lead_variant_afr = lead_afr,
      lead_variant_eur = lead_eur,
      lead_sign_agree = lead_sign_agree
    )
  })

  out_dt <- rbindlist(out_rows)
  fwrite(out_dt, opt$output_tsv, sep = "\t")
  cat("[run_matched_coloc] wrote", nrow(out_dt), "signal rows to", opt$output_tsv, "\n")
} else {
  # Write empty TSV with header for no-signal / error cases
  empty_dt <- data.table(
    signal_id = character(),
    pph4 = numeric(),
    pph3 = numeric(),
    pph2 = numeric(),
    pph1 = numeric(),
    pph0 = numeric(),
    cs_afr_size = integer(),
    cs_eur_size = integer(),
    lead_variant_afr = character(),
    lead_variant_eur = character(),
    lead_sign_agree = integer()
  )
  fwrite(empty_dt, opt$output_tsv, sep = "\t")
  cat("[run_matched_coloc] status=", result$status,
      "— wrote empty TSV to", opt$output_tsv, "\n")
}

cat("[run_matched_coloc] done. status=", result$status, "\n")
