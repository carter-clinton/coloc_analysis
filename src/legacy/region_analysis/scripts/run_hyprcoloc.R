#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(data.table)
  library(jsonlite)
})

parse_args_fallback <- function(args) {
  out <- list()
  i <- 1
  while (i <= length(args)) {
    key <- args[[i]]
    if (startsWith(key, "--")) {
      key <- sub("^--", "", key)
      val <- NA_character_
      if (i < length(args)) {
        val <- args[[i + 1]]
      }
      out[[key]] <- val
      i <- i + 2
    } else {
      i <- i + 1
    }
  }
  out
}

opt <- list()
if (requireNamespace("optparse", quietly = TRUE)) {
  library(optparse)
  option_list <- list(
    make_option("--manifest", type = "character"),
    make_option("--group-id", type = "character"),
    make_option("--output", type = "character")
  )
  opt <- parse_args(OptionParser(option_list = option_list))
} else {
  opt <- parse_args_fallback(commandArgs(trailingOnly = TRUE))
}

group_id <- opt$group_id
if (is.null(group_id) && "group-id" %in% names(opt)) {
  group_id <- opt[["group-id"]]
}
if (is.null(opt$manifest) || is.null(group_id) || is.null(opt$output)) {
  stop("--manifest, --group-id, and --output are required", call. = FALSE)
}

read_header <- function(path) {
  cmd <- sprintf("zcat -f %s | head -n 1", shQuote(path))
  header <- tryCatch(system(cmd, intern = TRUE), error = function(e) character(0))
  if (length(header) == 0) {
    return(NULL)
  }
  strsplit(header[1], "\t")[[1]]
}

read_sumstats <- function(path, chr, start, end) {
  if (grepl("\\.(bgz|gz)$", path, ignore.case = TRUE)) {
    tabix_bin <- Sys.getenv("TABIX_BIN", "tabix")
    region <- sprintf("%s:%s-%s", chr, start, end)
    cmd <- sprintf("%s -h %s %s", tabix_bin, shQuote(path), region)
    header <- read_header(path)
    dt <- tryCatch(
      fread(cmd = cmd, sep = "\t", header = FALSE),
      error = function(e) NULL
    )
    if (!is.null(dt)) {
      if (!is.null(header) && length(header) == ncol(dt)) {
        setnames(dt, header)
      }
      if (nrow(dt) > 0) {
        return(dt)
      }
    }
    return(fread(cmd = sprintf("gunzip -c %s", shQuote(path)), sep = "\t"))
  }
  fread(path, sep = "\t")
}

manifest <- fread(opt$manifest, sep = "\t", data.table = FALSE)
row <- manifest[manifest$group_id == group_id, , drop = FALSE]
if (nrow(row) != 1) {
  stop(sprintf("group_id %s not found", group_id))
}

if (!(row$status[1] %in% c("ready", "ready_secondary"))) {
  placeholder <- list(
    group_id = row$group_id[1],
    base_region = row$base_region[1],
    ancestry = row$ancestry[1],
    status = row$status[1],
    n_shared_snps = row$n_shared_snps[1]
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(placeholder, opt$output, auto_unbox = TRUE, pretty = TRUE)
  quit(save = "no", status = 0)
}

traits <- strsplit(row$traits_included[1], ",")[[1]]
paths <- strsplit(row$paths[1], ";")[[1]]
path_map <- setNames(
  vapply(paths, function(x) strsplit(x, "=")[[1]][2], character(1)),
  vapply(paths, function(x) strsplit(x, "=")[[1]][1], character(1))
)

chr <- as.character(row$chr[1])
start <- as.numeric(row$start[1])
end <- as.numeric(row$end[1])

merge_list <- list()
for (trait in traits) {
  path <- path_map[[trait]]
  dt <- read_sumstats(path, chr, start, end)
  if (!("SNP_ID" %in% names(dt))) {
    if ("CHR" %in% names(dt) && "POS" %in% names(dt)) {
      dt[, SNP_ID := paste0(gsub("^chr", "", CHR, ignore.case = TRUE), ":", POS)]
    } else {
      next
    }
  }
  dt[, CHR := gsub("^chr", "", CHR, ignore.case = TRUE)]
  dt[, CHR := as.character(CHR)]
  dt[, POS := as.numeric(POS)]
  dt <- dt[CHR == chr & POS >= start & POS <= end]
  if (nrow(dt) == 0) next
  if (!("BETA" %in% names(dt)) || !("SE" %in% names(dt))) next
  dt <- dt[!is.na(BETA) & !is.na(SE)]
  dt[, SNP_KEY := paste0(CHR, ":", POS)]
  dt <- dt[, .(SNP_KEY, BETA, SE)]
  setnames(dt, c("BETA", "SE"), c(paste0("BETA_", trait), paste0("SE_", trait)))
  merge_list[[trait]] <- dt
}

if (length(merge_list) < 3) {
  placeholder <- list(
    group_id = row$group_id[1],
    base_region = row$base_region[1],
    ancestry = row$ancestry[1],
    status = "insufficient_traits",
    n_shared_snps = 0
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(placeholder, opt$output, auto_unbox = TRUE, pretty = TRUE)
  quit(save = "no", status = 0)
}

merged <- Reduce(function(x, y) merge(x, y, by = "SNP_KEY"), merge_list)
min_shared <- ifelse(row$status[1] == "ready_secondary", 50, 200)
if (nrow(merged) < min_shared) {
  placeholder <- list(
    group_id = row$group_id[1],
    base_region = row$base_region[1],
    ancestry = row$ancestry[1],
    status = "low_overlap",
    n_shared_snps = nrow(merged)
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(placeholder, opt$output, auto_unbox = TRUE, pretty = TRUE)
  quit(save = "no", status = 0)
}

if (!requireNamespace("hyprcoloc", quietly = TRUE)) {
  placeholder <- list(
    group_id = row$group_id[1],
    base_region = row$base_region[1],
    ancestry = row$ancestry[1],
    status = "error",
    error = "hyprcoloc_not_installed",
    n_shared_snps = nrow(merged)
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(placeholder, opt$output, auto_unbox = TRUE, pretty = TRUE)
  quit(save = "no", status = 0)
}

beta_cols <- paste0("BETA_", traits)
se_cols <- paste0("SE_", traits)
betas <- as.matrix(merged[, ..beta_cols])
ses <- as.matrix(merged[, ..se_cols])

res <- tryCatch({
  hyprcoloc::hyprcoloc(betas, ses, trait.names = traits)
}, error = function(e) {
  list(error = e$message)
})
if (inherits(res, "hyprcoloc")) {
  class(res) <- NULL
}

summary_fields <- list(candidate = NA, posterior = NA, traits_used = NA)
if (is.list(res) && !"error" %in% names(res)) {
  if (!is.null(res$results) && is.data.frame(res$results) && nrow(res$results) > 0) {
    top <- res$results[1, , drop = FALSE]
    if ("candidate" %in% names(top)) {
      summary_fields$candidate <- as.character(top$candidate[1])
    } else if ("candidate_snp" %in% names(top)) {
      summary_fields$candidate <- as.character(top$candidate_snp[1])
    }
    if ("posterior" %in% names(top)) {
      summary_fields$posterior <- as.numeric(top$posterior[1])
    } else if ("posterior.prob" %in% names(top)) {
      summary_fields$posterior <- as.numeric(top$posterior.prob[1])
    }
    if ("traits" %in% names(top)) {
      summary_fields$traits_used <- as.character(top$traits[1])
    } else if ("traits.coloc" %in% names(top)) {
      summary_fields$traits_used <- as.character(top$traits.coloc[1])
    }
  } else if (!is.null(res$summary) && is.data.frame(res$summary) && nrow(res$summary) > 0) {
    top <- res$summary[1, , drop = FALSE]
    if ("candidate" %in% names(top)) {
      summary_fields$candidate <- as.character(top$candidate[1])
    }
    if ("posterior" %in% names(top)) {
      summary_fields$posterior <- as.numeric(top$posterior[1])
    }
    if ("traits" %in% names(top)) {
      summary_fields$traits_used <- as.character(top$traits[1])
    }
  }
}

output <- list(
  group_id = row$group_id[1],
  base_region = row$base_region[1],
  ancestry = row$ancestry[1],
  traits = traits,
  n_shared_snps = nrow(merged),
  summary = summary_fields,
  result = res
)
dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
write_json(output, opt$output, auto_unbox = TRUE, pretty = TRUE)
