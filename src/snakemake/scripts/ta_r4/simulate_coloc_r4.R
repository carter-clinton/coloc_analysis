#!/usr/bin/env Rscript
# E8 simulation-calibration harness (D-23, D-26): one (region, scenario, generation panel) job -> TSV of reps x arms.
#   z ~ N(R sqrt(n) b, R), R = the PSD-clipped generation-panel window, drawn via its eigen-decomposition.
#   A1: coloc.abf on beta = z/sqrt(n), varbeta = 1/n (quant, sdY 1). A2: SuSiE with R = I. A3: SuSiE with the fit panel.
#   SuSiE = the frozen run_susie_rss.R ladder (its functions are parsed out of the frozen file, not copied);
#   coloc = run_coloc_pair_r4.R::coloc_pair_core. Run from the repo root. --reps-override is for smoke runs only.
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
  library(susieR)
  library(coloc)
  library(yaml)
})

FROZEN_SCRIPT <- "src/legacy/region_analysis/scripts/run_susie_rss.R"
COLOC_SCRIPT <- "src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R"
COLUMNS <- c("region", "scenario", "gen_panel", "rep", "seed", "arm", "method", "pp_h0", "pp_h1", "pp_h2", "pp_h3",
             "pp_h4", "pp_h4_max", "n_cs_a", "n_cs_b", "causal_a", "causal_b", "r2_causal")

sim_fail <- function(code, ...) stop(sprintf("%s: %s", code, sprintf(...)), call. = FALSE)

frozen_functions <- function(path = FROZEN_SCRIPT, want = c("%||%", "regularize_ld", "run_susie_with_ladder")) {
  env <- new.env(parent = globalenv())
  for (e in parse(path, keep.source = FALSE)) {
    if (is.call(e) && identical(e[[1]], as.name("<-")) && is.name(e[[2]]) && as.character(e[[2]]) %in% want) {
      eval(e, env)
    }
  }
  miss <- setdiff(want, ls(env, all.names = TRUE))
  if (length(miss)) sim_fail("FROZEN_FUNCTIONS", "%s not found in %s", toString(miss), path)
  env
}

coloc_functions <- function(path = COLOC_SCRIPT) {
  env <- new.env(parent = globalenv())
  sys.source(path, envir = env)
  if (!exists("coloc_pair_core", envir = env, inherits = FALSE)) sim_fail("COLOC_CORE", "no coloc_pair_core in %s", path)
  env
}

FZ <- frozen_functions()
CP <- coloc_functions()
`%||%` <- get("%||%", envir = FZ)

# The frozen script's policy reads and defaults (run_susie_rss.R: L_DEFAULT .. LD_REG_EPS).
read_policy <- function(path) {
  s <- yaml::read_yaml(path)$susie
  list(L = s$L %||% 10L, max_iter_primary = s$max_iter_primary %||% 100L, max_iter_retry = s$max_iter_retry %||% 200L,
       ld_regularization_eps = s$ld_regularization_eps %||% 1e-4)
}

# The frozen script's fit path: symmetrize + unit diagonal, ladder, identity fallback, annotate_susie.
fit_frozen <- function(FZ, z, R, n, pol, coverage, snp_names) {
  R <- (R + t(R)) / 2
  diag(R) <- 1
  lp <- list(L = min(pol$L, length(z)), coverage = coverage, max_iter_primary = pol$max_iter_primary,
             max_iter_retry = pol$max_iter_retry, ld_regularization_eps = pol$ld_regularization_eps)
  lo <- FZ$run_susie_with_ladder(z = z, R = R, policy = lp, n = n)
  fit <- lo$fit
  status <- lo$status
  if (is.null(fit)) {
    lo <- FZ$run_susie_with_ladder(z = z, R = diag(length(z)), policy = lp, n = n)
    fit <- lo$fit
    status <- paste(lo$status, "identity_fallback", sep = ";")
  }
  if (!inherits(fit, "susie")) class(fit) <- c("susie", class(fit))
  dimnames(R) <- list(snp_names, snp_names)
  fit <- tryCatch(coloc:::annotate_susie(fit, snp_names, R), error = function(e) fit)
  list(fit = fit, status = status)
}

psd_generator <- function(R) {
  e <- eigen((R + t(R)) / 2, symmetric = TRUE)
  lam <- pmax(e$values, 0)
  list(R = e$vectors %*% (lam * t(e$vectors)), F = e$vectors %*% diag(sqrt(lam), length(lam)))
}

# k draws of z ~ N(R sb, R), sb = sqrt(n) b; a vector when k = 1, else an m x k matrix.
draw_z <- function(gen, sb, k = 1L) {
  m <- nrow(gen$R)
  Z <- as.vector(gen$R %*% sb) + gen$F %*% matrix(rnorm(m * k), m, k)
  if (k == 1L) as.vector(Z) else Z
}

window_idx <- function(m, w) {
  if (m <= w) return(seq_len(m))
  s <- (m - w) %/% 2L + 1L
  s:(s + w - 1L)
}

stable_index <- function(cfg, region, scenario, gen, rep) {
  dims <- list(sort(unlist(cfg$regions), method = "radix"), sort(names(cfg$scenarios), method = "radix"),
               sort(names(cfg$gen_panels), method = "radix"))
  at <- mapply(match, list(region, scenario, gen), dims)
  if (anyNA(at)) sim_fail("STABLE_INDEX", "unknown (%s, %s, %s)", region, scenario, gen)
  if (rep < 1 || rep > cfg$reps) sim_fail("STABLE_INDEX", "rep %s outside 1..%d", rep, cfg$reps)
  ((at[1] - 1) * length(dims[[2]]) * length(dims[[3]]) + (at[2] - 1) * length(dims[[3]]) + (at[3] - 1)) * cfg$reps + rep
}

# Ordered (c1, c2), c1 != c2, with r^2 in the closed bin under R_fit.
qualifying_pairs <- function(R_fit, bin) {
  r2 <- R_fit^2
  p <- which(r2 >= bin[1] & r2 <= bin[2] & row(r2) != col(r2), arr.ind = TRUE)
  p[order(p[, 1], p[, 2]), , drop = FALSE]
}

choose_causal <- function(type, m, pairs) {
  if (type == "H0") return(list(a = NA_integer_, b = NA_integer_))
  if (type == "H4") { c1 <- sample.int(m, 1L); return(list(a = c1, b = c1)) }
  if (type == "H3") { k <- sample.int(nrow(pairs), 1L); return(list(a = pairs[k, 1], b = pairs[k, 2])) }
  sim_fail("SCENARIO", "unknown scenario type %s", type)
}

load_panel <- function(path, want_dir, what) {
  if (basename(dirname(path)) != want_dir) sim_fail("PANEL", "%s %s is not under %s/", what, path, want_dir)
  p <- readRDS(path)
  if (is.null(p$R) || nrow(p$R) != ncol(p$R) || nrow(p$R) != nrow(p$variants) || anyNA(p$R)) {
    sim_fail("PANEL", "%s %s: R missing, non-square, NA, or not matching variants", what, path)
  }
  p
}

make_context <- function(fit_panel, gen_panel, gen, scenario, region, config, priors, policy, coverage,
                         reps_override = NA_integer_) {
  cfg <- yaml::read_yaml(config)
  for (k in c("n_per_trait", "causal_z", "reps", "seed_base", "window_variants")) {
    if (length(cfg[[k]]) != 1 || !is.finite(as.numeric(cfg[[k]])) || as.numeric(cfg[[k]]) <= 0) {
      sim_fail("CONFIG", "%s must be one positive number in %s", k, config)
    }
  }
  if (!scenario %in% names(cfg$scenarios)) sim_fail("SCENARIO", "%s not in %s", scenario, config)
  if (!gen %in% names(cfg$gen_panels)) sim_fail("GEN", "%s not in %s", gen, config)
  if (!region %in% unlist(cfg$regions)) sim_fail("REGION", "%s not in %s", region, config)
  pf <- load_panel(fit_panel, cfg$fit_panel, "fit panel")
  pg <- load_panel(gen_panel, cfg$gen_panels[[gen]], "generation panel")
  cols <- c("CHR", "POS", "REF", "ALT")
  if (!isTRUE(all.equal(as.data.frame(pf$variants)[cols], as.data.frame(pg$variants)[cols], check.attributes = FALSE))) {
    sim_fail("PANEL", "fit and generation panels have different variant frames for %s", region)
  }
  w <- window_idx(nrow(pf$R), cfg$window_variants)
  v <- as.data.frame(pf$variants)[w, cols]
  keys <- sprintf("%s:%s", v$CHR, format(as.integer(v$POS), scientific = FALSE, trim = TRUE))
  if (anyDuplicated(keys)) sim_fail("PANEL", "duplicate CHR:POS in the %s window", region)
  R_fit <- pf$R[w, w]
  R_gen <- pg$R[w, w]
  rm(pf, pg)
  pri <- yaml::read_yaml(priors)
  sc <- cfg$scenarios[[scenario]]
  pairs <- if (sc$type == "H3") qualifying_pairs(R_fit, unlist(sc$r2_bin)) else NULL
  list(cfg = cfg, region = region, scenario = scenario, type = sc$type, gen = gen, n = as.numeric(cfg$n_per_trait),
       causal_z = as.numeric(cfg$causal_z), variants = v, keys = keys, R_fit = R_fit, gen_R = psd_generator(R_gen),
       pairs = pairs, pol = read_policy(policy), coverage = coverage,
       pri = list(p1 = as.numeric(pri$p1), p2 = as.numeric(pri$p2), p12 = as.numeric(pri[[cfg$p12_key]]),
                  overlap_min = as.numeric(pri$overlap_min), trim = isTRUE(pri$trim_by_posterior)),
       reps = if (is.na(reps_override)) cfg$reps else reps_override)
}

run_rep <- function(ctx, rep) {
  seed <- ctx$cfg$seed_base + stable_index(ctx$cfg, ctx$region, ctx$scenario, ctx$gen, rep)
  set.seed(seed)
  m <- length(ctx$keys)
  cz <- choose_causal(ctx$type, m, ctx$pairs)
  sb <- function(c1) { x <- numeric(m); if (!is.na(c1)) x[c1] <- ctx$causal_z; x }
  z <- list(a = draw_z(ctx$gen_R, sb(cz$a)), b = draw_z(ctx$gen_R, sb(cz$b)))
  rows <- lapply(z, function(zz) data.table(BETA = zz / sqrt(ctx$n), SE = 1 / sqrt(ctx$n)))
  ti <- list(type = "quant", sdY = 1, N = ctx$n)
  fits <- list(A2 = lapply(z, fit_frozen, FZ = FZ, R = diag(m), n = ctx$n, pol = ctx$pol, coverage = ctx$coverage,
                           snp_names = ctx$keys),
               A3 = lapply(z, fit_frozen, FZ = FZ, R = ctx$R_fit, n = ctx$n, pol = ctx$pol, coverage = ctx$coverage,
                           snp_names = ctx$keys))
  side <- function(fit, t) list(fit = fit, keys = ctx$keys, rows = rows[[t]])
  res <- list(A1 = CP$coloc_pair_core(side(NULL, "a"), side(NULL, "b"), ti, ti, ctx$pri, "A1_matched"),
              A2 = CP$coloc_pair_core(side(fits$A2$a$fit, "a"), side(fits$A2$b$fit, "b"), ti, ti, ctx$pri, "susie"),
              A3 = CP$coloc_pair_core(side(fits$A3$a$fit, "a"), side(fits$A3$b$fit, "b"), ti, ti, ctx$pri, "susie"))
  key_of <- function(i) if (is.na(i)) NA_character_ else ctx$keys[i]
  r2 <- if (is.na(cz$a)) NA_real_ else ctx$R_fit[cz$a, cz$b]^2
  out <- rbindlist(lapply(names(res), function(arm) {
    x <- res[[arm]]
    data.table(region = ctx$region, scenario = ctx$scenario, gen_panel = ctx$gen, rep = as.integer(rep),
               seed = as.integer(seed), arm = arm, method = x$method, pp_h0 = x$pp[1], pp_h1 = x$pp[2],
               pp_h2 = x$pp[3], pp_h3 = x$pp[4], pp_h4 = x$pp[5], pp_h4_max = x$out$pp_h4_max,
               n_cs_a = x$out$n_cs_a, n_cs_b = x$out$n_cs_b, causal_a = key_of(cz$a), causal_b = key_of(cz$b),
               r2_causal = r2)
  }))
  setcolorder(out, COLUMNS)
  list(rows = out, fits = fits, z = z)
}

main <- function() {
  opt <- parse_args(OptionParser(option_list = list(
    make_option("--fit-panel"), make_option("--gen-panel"), make_option("--gen"), make_option("--scenario"),
    make_option("--region"), make_option("--config"), make_option("--priors"), make_option("--policy"),
    make_option("--credible-set", type = "double", default = 0.95), make_option("--out"),
    make_option("--reps-override", type = "integer", default = NA_integer_)
  )))
  for (k in c("fit-panel", "gen-panel", "gen", "scenario", "region", "config", "priors", "policy", "out")) {
    if (is.null(opt[[k]]) || !nzchar(opt[[k]])) sim_fail("ARGS", "--%s is required", k)
  }
  ctx <- make_context(opt$`fit-panel`, opt$`gen-panel`, opt$gen, opt$scenario, opt$region, opt$config, opt$priors,
                      opt$policy, opt$`credible-set`, opt$`reps-override`)
  status <- if (ctx$type == "H3" && nrow(ctx$pairs) == 0) "no_qualifying_pair" else "ok"
  n_reps <- if (status == "ok") ctx$reps else 0L
  rows <- vector("list", n_reps)
  for (k in seq_len(n_reps)) {
    rows[[k]] <- run_rep(ctx, k)$rows
    if (k %% 10L == 0L) message(sprintf("[simulate_coloc_r4] %s %s %s rep %d/%d", opt$region, opt$scenario, opt$gen,
                                        k, n_reps))
  }
  tab <- if (n_reps) rbindlist(rows) else setnames(data.table(matrix(character(0), 0, length(COLUMNS))), COLUMNS)
  head <- c(sprintf("# simulate_coloc_r4 region=%s scenario=%s gen_panel=%s", opt$region, opt$scenario, opt$gen),
            sprintf("# reps_override=%s", if (is.na(opt$`reps-override`)) "none" else opt$`reps-override`),
            sprintf("# status=%s", status),
            sprintf("# n_qualifying_pairs=%s", if (is.null(ctx$pairs)) "NA" else nrow(ctx$pairs)),
            sprintf("# window_variants=%d reps=%d config_sha256=%s", length(ctx$keys), n_reps,
                    digest::digest(file = opt$config, algo = "sha256")))
  dir.create(dirname(opt$out), recursive = TRUE, showWarnings = FALSE)
  tmp <- paste0(opt$out, ".tmp")
  writeLines(head, tmp)
  fwrite(tab, tmp, sep = "\t", append = TRUE, col.names = TRUE, na = "NA", quote = FALSE)
  invisible(file.rename(tmp, opt$out))
  cat(sprintf("[simulate_coloc_r4] %s %s %s status=%s reps=%d rows=%d\n", opt$region, opt$scenario, opt$gen, status,
              n_reps, nrow(tab)))
}

if (sys.nframe() == 0L) main()
