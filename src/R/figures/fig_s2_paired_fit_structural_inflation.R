# fig_s2_paired_fit_structural_inflation.R — Track A Figure S2 (paired-fit structural inflation)
#
# Purpose: Quantify the structural posterior shifts between identity-LD and
#   real-LD SuSiE-RSS fine-mapping at the 48 paired non-empty fits — the
#   measurement that backs the audit-v2 §HQ3 Conclusion-1 reframe ("structural
#   posterior shifts": PIP redistribution and lead-variant rank instability).
#   Computed entirely from on-disk per-fit JSONs; no LSF, no re-SuSiE fire.
#
# Closes AUDIT-REVIEW-V2-2026-04-26.md §HQ2 ("Quantify the structural inflation
# claim before submission") under the constraints of the audit-v2 overnight
# revision sweep (no LSF, no data egress, no OSF portal action).
#
# Per-pair metrics (computed for each of 48 paired non-empty pairs):
#   1. PIP-of-top-variant per branch -> Delta = real - identity
#   2. Lead-variant rank: position of identity-LD's top variant in real-LD's
#      PIP-sorted vector (1 = same lead; 'absent' = identity-LD lead not in
#      real-LD CSs)
#   3. Credible-set member Jaccard: greedy argmax-overlap CS pairing,
#      aggregated as max-per-fit Jaccard
#
# Data sources (read at runtime; cross-checked vs disk-truth):
#   results/fine_mapping/susie/*.json                  (96 real-LD JSONs)
#   results_identity_ld/fine_mapping/susie/*.json      (95 identity-LD JSONs)
#   Pair-key = filename stem {trait}.{ancestry}.{region_id} (identical across
#   trees, verified at runtime).
#
# Authoritative ledger: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
#   (Wave 3 commit 11 appends a "Paired-fit structural inflation
#    (Figure S2, 2026-04-27) -- LIVE" block carrying the locked scalars
#    emitted by this script to stdout.)
#
# Outputs:
#   docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.pdf
#     (cairo_pdf, 180 mm x 140 mm)
#   docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.png
#     (600 dpi, 180 mm x 140 mm)
#
# Stdout (captured by the orchestrator for the FROZEN-NUMBERS LIVE block):
#   FROZEN_BEGIN ... FROZEN_END markers around a tribble-format block.
#
# Render env: /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
#   (R 4.4.2, ggplot2 4.0.1, jsonlite, dplyr, tidyr, scales, patchwork, cairo)
#
# Invocation (from project root):
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
#     src/R/figures/fig_s2_paired_fit_structural_inflation.R
#
# Disk-truth assertions (hard-fail to catch silent drift):
#   - real-LD non-empty count == 51
#   - identity-LD non-empty count == 48
#   - paired non-empty count == 48 (the audit-v2 invariant)
#
# Author: Carter K. Clinton -- 2026-04-27 (built quick-260427-azv;
#         audit-v2 sweep; closes AUDIT-REVIEW-V2 HQ2).

suppressPackageStartupMessages({
  library(jsonlite)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(scales)
  library(patchwork)
})

`%||%` <- function(a, b) if (is.null(a)) b else a

# --- Paths --------------------------------------------------------------------

PROJECT_ROOT <- normalizePath(getwd(), mustWork = TRUE)
if (!dir.exists(file.path(PROJECT_ROOT, "results", "fine_mapping", "susie"))) {
  stop(sprintf("[fig_s2] expected to be run from project root; cwd=%s missing results/fine_mapping/susie", PROJECT_ROOT))
}

REAL_DIR     <- file.path(PROJECT_ROOT, "results",              "fine_mapping", "susie")
IDENT_DIR    <- file.path(PROJECT_ROOT, "results_identity_ld",  "fine_mapping", "susie")
OUT_PDF      <- file.path(PROJECT_ROOT, "docs", "manuscript", "figures",
                          "fig_s2_paired_fit_structural_inflation.pdf")
OUT_PNG      <- file.path(PROJECT_ROOT, "docs", "manuscript", "figures",
                          "fig_s2_paired_fit_structural_inflation.png")

stopifnot(dir.exists(REAL_DIR), dir.exists(IDENT_DIR))

# --- Load + filter to non-empty -----------------------------------------------

read_fit <- function(path) {
  d <- tryCatch(fromJSON(path, simplifyVector = FALSE),
                error = function(e) NULL)
  if (is.null(d)) return(NULL)
  cs <- d$credible_sets
  if (is.null(cs) || length(cs) == 0) return(NULL)
  list(
    path   = path,
    key    = sub("\\.json$", "", basename(path)),
    trait  = d$trait,
    anc    = d$ancestry,
    region = d$region_id,
    n_cs   = length(cs),
    pip    = unlist(d$pip),
    cs     = cs,
    niter  = d$niter,
    L_sat  = isTRUE(d$L_saturated),
    conv   = d$convergence_status %||% d$status %||% NA_character_,
    ld_overlap_fraction = d$ld_overlap_fraction %||% NA_real_
  )
}

real_files  <- list.files(REAL_DIR,  pattern = "\\.json$", full.names = TRUE)
ident_files <- list.files(IDENT_DIR, pattern = "\\.json$", full.names = TRUE)

real_all  <- lapply(real_files,  read_fit)
ident_all <- lapply(ident_files, read_fit)
real_all  <- Filter(Negate(is.null), real_all)
ident_all <- Filter(Negate(is.null), ident_all)

names(real_all)  <- vapply(real_all,  `[[`, character(1), "key")
names(ident_all) <- vapply(ident_all, `[[`, character(1), "key")

# --- Disk-truth assertions ----------------------------------------------------

real_total  <- length(real_files)
ident_total <- length(ident_files)
real_ne     <- length(real_all)
ident_ne    <- length(ident_all)
paired_keys <- intersect(names(real_all), names(ident_all))
n_paired    <- length(paired_keys)

message(sprintf("[fig_s2] real total: %d  non-empty: %d", real_total, real_ne))
message(sprintf("[fig_s2] identity total: %d  non-empty: %d", ident_total, ident_ne))
message(sprintf("[fig_s2] paired non-empty: %d", n_paired))

stopifnot(real_total == 96)
stopifnot(ident_total == 95)
stopifnot(real_ne == 51)
stopifnot(ident_ne == 48)
stopifnot(n_paired == 48)

# --- Per-pair metric extraction -----------------------------------------------

cs_member_pos <- function(fit) {
  # Returns character vector of unique POS strings across all CSs.
  pos <- unlist(lapply(fit$cs, function(cs1) {
    vapply(cs1, function(v) as.character(v$POS %||% NA), character(1))
  }))
  unique(stats::na.omit(pos))
}

cs_per_set_pos <- function(fit) {
  # Returns list of character vectors (one per CS) of POS strings.
  lapply(fit$cs, function(cs1) {
    vapply(cs1, function(v) as.character(v$POS %||% NA), character(1))
  })
}

top_variant <- function(fit) {
  # Returns POS string of the highest-PIP variant within any CS.
  best_pos <- NA_character_
  best_pip <- -Inf
  for (cs1 in fit$cs) {
    for (v in cs1) {
      pip_v <- v$pip %||% NA_real_
      if (!is.na(pip_v) && pip_v > best_pip) {
        best_pip <- pip_v
        best_pos <- as.character(v$POS %||% NA)
      }
    }
  }
  list(pos = best_pos, pip = best_pip)
}

cs_jaccard <- function(a_set, b_set) {
  if (length(a_set) == 0 || length(b_set) == 0) return(0)
  length(intersect(a_set, b_set)) / length(union(a_set, b_set))
}

max_per_fit_jaccard <- function(real_fit, ident_fit) {
  # Greedy argmax-overlap CS pairing; aggregated as max-Jaccard per fit.
  rsets <- cs_per_set_pos(real_fit)
  isets <- cs_per_set_pos(ident_fit)
  if (length(rsets) == 0 || length(isets) == 0) return(0)
  # All-pairs Jaccard matrix
  jmat <- outer(seq_along(rsets), seq_along(isets),
                Vectorize(function(i, j) cs_jaccard(rsets[[i]], isets[[j]])))
  max(jmat)
}

build_row <- function(key) {
  rf <- real_all[[key]]
  if_ <- ident_all[[key]]
  rt  <- top_variant(rf)
  it  <- top_variant(if_)
  # Lead-variant rank: position of identity-LD's top variant within real-LD's
  # full CS-member set, ordered by PIP descending.
  real_pos_pip <- do.call(rbind, lapply(rf$cs, function(cs1) {
    do.call(rbind, lapply(cs1, function(v) {
      data.frame(pos = as.character(v$POS %||% NA),
                 pip = v$pip %||% NA_real_,
                 stringsAsFactors = FALSE)
    }))
  }))
  real_pos_pip <- real_pos_pip[order(-real_pos_pip$pip), , drop = FALSE]
  rank_in_real <- match(it$pos, real_pos_pip$pos)
  if (is.na(rank_in_real)) rank_in_real <- Inf
  data.frame(
    key             = key,
    trait           = rf$trait,
    anc             = rf$anc,
    region          = rf$region,
    pip_top_real    = rt$pip,
    pip_top_ident   = it$pip,
    delta_pip_top   = rt$pip - it$pip,
    lead_rank       = rank_in_real,
    max_jaccard     = max_per_fit_jaccard(rf, if_),
    n_cs_real       = rf$n_cs,
    n_cs_ident      = if_$n_cs,
    real_conv       = rf$conv,
    ident_conv      = if_$conv,
    ld_overlap_real = rf$ld_overlap_fraction,
    stringsAsFactors = FALSE
  )
}

paired <- do.call(rbind, lapply(paired_keys, build_row))
stopifnot(nrow(paired) == 48)

paired$rank_bin <- cut(
  paired$lead_rank,
  breaks = c(-Inf, 1, 5, 20, Inf),
  labels = c("rank=1", "rank 2-5", "rank 6-20", "rank >=21 OR absent"),
  right  = TRUE
)
# rank=Inf goes into the last bin; verify
stopifnot(all(!is.na(paired$rank_bin)))

# --- Locked scalars (emit to stdout for FROZEN-NUMBERS) ------------------------

scalars <- list(
  paired_n               = nrow(paired),
  delta_pip_median       = round(median(paired$delta_pip_top), 4),
  delta_pip_iqr_lo       = round(quantile(paired$delta_pip_top, 0.25), 4),
  delta_pip_iqr_hi       = round(quantile(paired$delta_pip_top, 0.75), 4),
  rank_eq_1_n            = sum(paired$lead_rank == 1),
  rank_eq_1_pct          = round(100 * mean(paired$lead_rank == 1), 1),
  rank_ge_21_or_absent_n = sum(paired$lead_rank >= 21 | is.infinite(paired$lead_rank)),
  rank_ge_21_or_absent_pct = round(100 * mean(paired$lead_rank >= 21 | is.infinite(paired$lead_rank)), 1),
  jaccard_ge_0_8_n       = sum(paired$max_jaccard >= 0.8),
  jaccard_ge_0_8_pct     = round(100 * mean(paired$max_jaccard >= 0.8), 1),
  jaccard_lt_0_5_n       = sum(paired$max_jaccard <  0.5),
  jaccard_lt_0_5_pct     = round(100 * mean(paired$max_jaccard <  0.5), 1)
)

cat("FROZEN_BEGIN\n")
for (k in names(scalars)) cat(sprintf("%s\t%s\n", k, scalars[[k]]))
cat("FROZEN_END\n")

# --- Plot panels --------------------------------------------------------------

theme_track_a <- theme_minimal(base_size = 9) +
  theme(
    plot.title       = element_text(face = "bold", size = 9.5),
    plot.subtitle    = element_text(size = 8, color = "grey30"),
    panel.grid.minor = element_blank(),
    plot.margin      = margin(4, 4, 4, 4)
  )

# (A) Histogram: PIP-of-top-variant Delta distribution
pA <- ggplot(paired, aes(x = delta_pip_top)) +
  geom_histogram(binwidth = 0.05, fill = "#3a6ea5", colour = "white", boundary = 0) +
  geom_vline(xintercept = 0, linetype = "dashed", colour = "grey40") +
  scale_x_continuous(limits = c(-1.05, 1.05), breaks = seq(-1, 1, 0.5)) +
  labs(title = "(A) PIP-of-top-variant: real - identity",
       subtitle = sprintf("median Delta = %.3f (n = %d paired)", scalars$delta_pip_median, scalars$paired_n),
       x = "Delta PIP (real - identity)", y = "fits") +
  theme_track_a

# (B) Lead-variant rank distribution
pB_df <- as.data.frame(table(paired$rank_bin))
names(pB_df) <- c("bin", "n")
pB_df$pct <- round(100 * pB_df$n / sum(pB_df$n), 1)
pB <- ggplot(pB_df, aes(x = bin, y = n)) +
  geom_col(fill = "#a93a3a", colour = "white") +
  geom_text(aes(label = sprintf("%d (%.0f%%)", n, pct)), vjust = -0.4, size = 3) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
  labs(title = "(B) Lead-variant rank under real-LD",
       subtitle = sprintf("identity-LD top variant's rank in real-LD (n = %d paired)", scalars$paired_n),
       x = NULL, y = "fits") +
  theme_track_a +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

# (C) Histogram: max-Jaccard distribution
pC <- ggplot(paired, aes(x = max_jaccard)) +
  geom_histogram(binwidth = 0.1, fill = "#3a8a4a", colour = "white", boundary = 0) +
  geom_vline(xintercept = c(0.5, 0.8), linetype = c("dashed", "dotted"), colour = "grey40") +
  scale_x_continuous(limits = c(-0.02, 1.02), breaks = seq(0, 1, 0.25)) +
  labs(title = "(C) Max per-fit credible-set Jaccard",
       subtitle = sprintf(">= 0.8: %d (%.0f%%)  |  < 0.5: %d (%.0f%%)",
                          scalars$jaccard_ge_0_8_n, scalars$jaccard_ge_0_8_pct,
                          scalars$jaccard_lt_0_5_n, scalars$jaccard_lt_0_5_pct),
       x = "max Jaccard", y = "fits") +
  theme_track_a

# (D) Per-pair scatter: identity vs real PIP-top
pD <- ggplot(paired, aes(x = pip_top_ident, y = pip_top_real)) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", colour = "grey50") +
  geom_point(aes(colour = max_jaccard, size = pmax(n_cs_real, n_cs_ident)),
             alpha = 0.85, stroke = 0) +
  scale_colour_viridis_c(name = "max Jacc",
                         limits = c(0, 1), breaks = seq(0, 1, 0.25)) +
  scale_size_continuous(name = "max(n_CS)",
                        breaks = c(1, 3, 5, 10), range = c(1.4, 5)) +
  scale_x_continuous(limits = c(0, 1.02)) +
  scale_y_continuous(limits = c(0, 1.02)) +
  labs(title = "(D) PIP-top per pair (n = 48)",
       subtitle = "diagonal = perfect agreement; below = real-LD lower",
       x = "identity-LD PIP-top", y = "real-LD PIP-top") +
  theme_track_a +
  theme(legend.position = "right",
        legend.box = "vertical",
        legend.key.size = unit(0.4, "cm"))

# --- Compose + save -----------------------------------------------------------

composed <- (pA | pB) / (pC | pD) +
  plot_annotation(
    title    = "Figure S2. Paired-fit structural inflation (n = 48 paired non-empty SuSiE-RSS fits)",
    subtitle = sprintf(
      "real-LD vs identity-LD per-fit: PIP redistribution, lead-variant rank, credible-set Jaccard. Source: results/fine_mapping/susie + results_identity_ld/fine_mapping/susie."
    ),
    theme    = theme(plot.title    = element_text(face = "bold", size = 11),
                     plot.subtitle = element_text(size = 8.5, colour = "grey30"))
  )

ggsave(OUT_PDF, plot = composed, device = cairo_pdf,
       width = 180, height = 140, units = "mm")
ggsave(OUT_PNG, plot = composed,
       width = 180, height = 140, units = "mm", dpi = 600)

message(sprintf("[fig_s2] wrote %s", OUT_PDF))
message(sprintf("[fig_s2] wrote %s", OUT_PNG))
message("[fig_s2] done.")
